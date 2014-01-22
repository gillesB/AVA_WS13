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
    CARDS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]

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
        self.token = False

    def run(self):
        self.info()
        self.read_connections_and_open_port()
        self.choose_new_neighbours(0)
        time.sleep(1)
        for i in range(self.amount_rounds):
            self.define_order_and_choose_role()
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
                    self.logger.info("Croupier hand: " + str(self.own_cards))
                    self.logger.info("Croupier result: " + str(self.final_result))
                    winners = self.determine_winners()
                    #Sende Gewinner
                    self.send_winners(winners)
                    #teile Ende der Runde mit
                    self.declare_end_of_round()
                else:
                    self.receive_messages()
            self.logger.info("END OF ROUND!")
        self.logger.info("I am going to kill myself.")
        sys.exit()

    def process_received_message(self, connection, message):
        if message.getAction() == "new_card?":
            amounts = self.count_cards()
            if min(amounts) > 16:
                self.send_message_over_socket(connection, self.stay_message)
            elif min(amounts) <= 16:
                self.send_message_over_socket(connection, self.hit_message)
        elif message.getAction() == "card":
            self.own_cards.append(message.getMessage())
        elif message.getAction() == "result?":
            amounts = self.count_cards()
            self.final_result = self.nearest_to_21(amounts)
            result_message = Message("result", self.final_result, sender=self._ID)
            self.send_message_over_socket(connection, result_message)
        elif message.getAction() == "end":
            self.end_of_round = True

    def choose_new_neighbours(self, amount_neighbours):
        '''
        Jeder Prozess ist zu jedem Prozess direkter Nachbar.
        self._ips_and_ports enthaelt alle IDs der anderen Prozesse ausser die eigene
        '''
        self._neighbours = self._ips_and_ports

    def define_order_and_choose_role(self):
        '''
        Leader election und Anordnung der Spieler basierend auf dem Echo Algorithmus.
        Der Prozess mit dem Token ist der Initiator des Echo Algo.
        Er sendet seine order an alle und erhàlt als Antwort die order von allen anderen.
        Danach sortiert er die Order und sendet die Tischordnung an alle Prozesse.
        Zu Schluss erfolgt das Auswaehlen der Rollen.
        '''
        my_order = self._system_random.random()
        self.order_of_players = dict()
        self.order_of_players[my_order] = self._ID
        my_order_message = Message("my_order", my_order, sender=self._ID)

        #Echo Algo
        if self.token:
            for neighbour in self._neighbours:
                answer_socket = self.send_message_to_id(my_order_message, neighbour)
                answer = self.receive_message_from_socket(answer_socket)
                self.order_of_players[answer.getMessage()] = answer.getSender()
            #sortiere dict nach key und gebe Liste mit den Values zurueck
            self.order_of_players = [value for (key, value) in sorted(self.order_of_players.items())]
            self.logger.info("Order of players: " + str(self.order_of_players))
            for neighbour in self._neighbours:
                my_order_message = Message("order", self.order_of_players, sender=self._ID)
                self.send_message_to_id(my_order_message, neighbour)
        else:
            socket, received_message = self.return_received_message()
            if received_message.getAction() == "my_order":
                self.send_message_over_socket(socket, my_order_message)
            else:
                self.logger.fatal("WTF are you sending??")
                sys.exit(1)

            socket, received_message = self.return_received_message()
            if received_message.getAction() == "order":
                self.order_of_players = received_message.getMessage()
            else:
                self.logger.fatal("WTF are you sending??")
                sys.exit(1)


        ID = self.order_of_players.pop(0)
        self.croupierID = ID
        self.logger.info("ID of croupier: " + str(self.croupierID))

        if self.croupierID == self._ID :
            self.role = self.CROUPIER
        else:
            self.choose_role(my_order)

        # Warte auf den Token ehe mit dem Austeilen der Karten begonnen werden kann
        if self.token and self.croupierID == self._ID:
            pass
        elif self.token:
            token_message = Message("token", "", sender=self._ID)
            self.send_message_to_id(token_message, self.croupierID)
            self.token = False
        elif self.croupierID == self._ID:
            socket, received_message = self.return_received_message()
            if received_message.getAction() == "token":
                self.token = True
            else:
                self.logger.fatal("WTF are you sending??")
                sys.exit(1)


    def choose_role(self, order):
        if int(order * 100) % 2 == 0:
            self.role = self.RISK
        else:
            self.role = self.SAFE
        self.logger.info("My role is:" + self.role)

    def receive_message_from_socket(self, socket):
        data = socket.recv(1024)
        if data:
            message = cPickle.loads(data)
            self.logger.info("direkt Antwort empfangen: " + message.printToString())
            return message
        return None

    def give_card_to_players(self):
        self.logger.debug("Giving cards to players.")
        for ID in self.order_of_players:
            card_message = self.draw_card()
            self.send_message_to_id(card_message, ID)
        self.logger.debug("Giving cards to players. Finished")

    def draw_card(self):
        number = self._system_random.choice(self.CARDS)
        card_message = Message("card", number, sender=self._ID)
        return card_message

    def draw_croupier_card(self):
        self.own_cards.append(self.draw_card().getMessage())

    def ask_players(self):
        new_card_message = Message("new_card?", "Do you want a new card?")
        amount_stayed = 0
        while amount_stayed < len(self.order_of_players):
            amount_stayed = 0
            for ID in self.order_of_players:
                #TODO NEED A TOKEN
                socket = self.send_message_to_id(new_card_message, ID)
                answer = self.receive_message_from_socket(socket)
                if answer.getAction() == "hit":
                    card = self.draw_card()
                    self.send_message_to_id(card, ID)
                elif answer.getAction() == "stay":
                    amount_stayed += 1
        self.logger.debug("All players stayed.")

    def draw_own_cards(self):
        amount = self.count_croupier_cards()
        while amount < 17:
            self.draw_croupier_card()
            amount = self.count_croupier_cards()
        return amount

    def count_cards(self):
        possible_results = [0]
        self.logger.info("I have got these cards: " + str(self.own_cards))
        for card_value in self.own_cards:
            new_results = []
            for i in range(len(possible_results)):
                if card_value == 11:
                    possible_results[i] += 1
                    new_results.append(possible_results[i] + 11)
                else:
                    possible_results[i] += card_value
            possible_results += new_results
        self.logger.info("My possible results are: " + str(possible_results))
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
        for ID in self.order_of_players:
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
            for ID, result in valid_result.items():
                if result > croupier_result:
                    winners.append(ID)
        return winners

    def send_winners(self, winners):
        winners_message = Message("winners", winners, sender=self._ID)
        for ID in self.order_of_players:
            self.send_message_to_id(winners_message, ID)

    def declare_end_of_round(self):
        self.end_of_round = True
        end_message = Message("end", "This is the end.", sender=self._ID)
        for ID in self.order_of_players:
            self.send_message_to_id(end_message, ID)

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











