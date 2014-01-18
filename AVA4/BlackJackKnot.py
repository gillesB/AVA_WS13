import cPickle
import sys
import time
from CodeBase.AbstractKnot import AbstractKnot
from CodeBase.Message import Message

__author__ = 'me'


class BlackJackKnot(AbstractKnot):
    CROUPIER = "croupier"
    RISK = "risk"
    SAFE = "safe"

    def __init__(self, ID, connections_filename, amount_rounds):
        super(BlackJackKnot, self).__init__(ID, connections_filename)
        self.amount_rounds = amount_rounds
        self.role = None
        self.end_of_round = False
        self.order_of_players = {}
        self.croupierID = None
        self.own_cards = []
        self.final_result = None
        self.results = {}
        self.stay_message = Message("stay", "No other card, please.", sender=self._ID)
        self.hit_message = Message("hit", "Hit me with another card.", sender=self._ID)

    def run(self):
        self.info()
        self.read_connections_and_open_port()
        self.choose_new_neighbours(0)
        time.sleep(1)
        for i in range(self.amount_rounds):
            self.choose_role()
            self.define_order()
            self.end_of_round = False
            self.own_cards = []
            while not self.end_of_round:
                if self.role == self.CROUPIER:
                    # Spieler erhalten zwei Anfangskarten, Croupier eine
                    self.give_card_to_players()
                    self.draw_croupier_card()
                    self.give_card_to_players()
                    #Bediene Spieler
                    self.ask_players()
                    #Ziehe eigne zweite Karte
                    self.draw_croupier_card()
                    #Ziehe weitere eigene Karten
                    self.final_result = self.draw_own_cards()
                    self.results[self._ID] = self.final_result
                    #Erhalte Resultat von Spielern
                    self.retrieve_results()
                    #Ermittle Gewinner
                    winners = self.determine_winner()
                    #Sende Gewinner
                    self.send_winners(winners)
                else:
                    self.receive_messages()

    def process_received_message(self, connection, message):
        if message.getAction() == "croupier":
            self.croupierID = message.getSender()
            order = self._system_random.randint(0, 100)
            answer = Message("player", order, sender=self._ID)
            self.send_message_over_socket(connection, answer)
        elif message.getAction() == "new_card?":
            amounts = self.count_cards()
            if 21 in amounts:
                self.send_message_over_socket(connection, self.stay_message)
            elif min(amounts) <= 16:
                self.send_message_over_socket(connection, self.hit_message)
        elif message.getAction() == "result?":
            amounts = self.count_cards()
            self.final_result = self.nearest_to_21(amounts)

    def choose_new_neighbours(self, amount_neighbours):
        '''
        Jeder Prozess ist zu jedem Prozess direkter Nachbar.
        self._ips_and_ports enthaelt alle IDs der anderen Prozesse ausser die eigene
        '''
        self._neighbours = self._ips_and_ports

    def choose_role(self):
        if int(self._ID) == 0:
            self.role = self.CROUPIER
            self.croupierID = self._ID
        elif int(self._ID) % 2 == 0:
            self.role = self.RISK
        else:
            self.role = self.SAFE
        self.logger.debug("My role is:"+ self.role)

    def define_order(self):
        if self.role == self.CROUPIER:
            self.order_of_players = {}
            for neighbour in self._neighbours:
                init_message = Message("croupier", "I am the croupier", sender=self._ID)
                socket = self.send_message_to_id(init_message, neighbour)
                answer = self.receive_message_from_socket(socket)
                self.order_of_players[answer.getMessage()] = neighbour
            sorted(self.order_of_players)
            self.logger.debug("Order of players: " + str(self.order_of_players))

    def receive_message_from_socket(self, socket):
        data = socket.recv(1024)
        if data:
            message = cPickle.loads(data)
            self.logger.info("empfangen: " + message.printToString())
            return message
        return None

    def give_card_to_players(self):
        self.logger.debug("Giving cards to players.")
        for ID in self.order_of_players.values():
            card_message = self.draw_card()
            self.send_message_to_id(card_message, ID)
        self.logger.debug("Giving cards to players. Finished")

    def draw_card(self):
        number = self._system_random.randint(2,11)
        card_message = Message("card", number, sender=self._ID)
        return card_message

    def draw_croupier_card(self):
        self.own_cards.append(self.draw_card().getMessage())

    def ask_players(self):
        new_card_message = Message("new_card?", "Do you want a new card?")
        amount_reste = 0
        while amount_reste == len(self.order_of_players):
            for ID in self.order_of_players.values():
                socket = self.send_message_to_id(new_card_message, ID)
                answer = self.receive_message_from_socket(socket)
                if answer.getAction() == "hit":
                    card = self.draw_card()
                    self.send_message_to_id(card, ID)
                else:
                    amount_reste += 1
            amount_reste = 0
        self.logger.debug("All players stayed.")

    def draw_own_cards(self):
        amount = self.count_croupier_cards()
        while amount < 17:
            self.draw_croupier_card()
            amount = self.count_croupier_cards()
        return amount

    def count_cards(self):
        possible_results = [0]
        for card_value in self.own_cards:
            new_results = []
            for i in len(possible_results):
                if card_value == 11:
                    possible_results[i] += 1
                    new_results.append(possible_results[i] + 11)
                else:
                    possible_results[i] += card_value
            possible_results.append(new_results)
        self.logger.debug("My possible results are: " + str(possible_results))
        return possible_results

    def count_croupier_cards(self):
        amount = sum(self.own_cards)
        if amount > 21 and 11 in self.own_cards:
            amount = 0
            for card_value in self.own_cards:
                if card_value == 11:
                    amount += 1
                else:
                    amount += card_value
        return amount

    def retrieve_results(self):
        result_message = Message("result?", "What is your result?")
        self.results = {}
        for ID in self.order_of_players.values():
            socket = self.send_message_to_id(result_message, ID)
            answer = self.receive_message_from_socket(socket)
            self.results[ID] = answer.getMessage()

    def determine_winners(self):
        overdraw = []
        valid_result = {}
        for ID, result in self.results.items():
            if result is None or result > 21:
                overdraw.append(ID)
            else:
                valid_result[ID] = result

        winners = []
        tie = []
        if self._ID in overdraw:
            winners = valid_result.values()
        else:
            croupier_result = self.final_result
            for ID, result in self.valid_result.items():
                if result > croupier_result:
                    winners.append(ID)
        return winners

    def send_winners(self, winners):
        winners_message = Message("winners", winners, sender=self._ID)
        for ID in self.order_of_players.values():
            self.send_message_to_id(winners_message, ID)

    @staticmethod
    def nearest_to_21(amounts):
        final_result = None
        difference = sys.maxint
        for result in amounts:
            temp_diff = 21 - result
            if 0 <= temp_diff < difference:
                final_result = result
                difference = temp_diff
        return final_result











