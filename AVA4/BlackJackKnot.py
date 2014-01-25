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
        self.order_of_players = []
        self.croupier_id = None
        self.own_cards = []
        self.final_result = None
        self.results = {}
        self.token = False
        self.croupier_card = None

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
                    self.execution_croupier()
                else:
                    self.execution_player()
            self.logger.info("END OF ROUND!")
        self.logger.info("I am going to kill myself.")
        sys.exit()

    def execution_player(self):
        #draw first card
        self.wait_for_token()
        self.draw_single_card()
        self.send_token_to_the_left()

        #draw second card
        self.wait_for_token()
        self.draw_single_card()
        self.send_token_to_the_left()

        #receive card from croupier
        self.receive_messages()

        #draw_cards
        self.wait_for_token()
        self.draw_more_cards()
        self.send_token_to_the_left()

        #get result from croupier
        #answer croupier if win,loose,tie
        self.receive_messages()
        #get final result from croupier
        self.receive_messages()

    def execution_croupier(self):
        #send token and wait till it returns
        self.send_token_to_the_left()
        self.wait_for_token()

        #the players just draw their first card. Draw own card.
        self.draw_single_card()

        #send token and wait till it returns
        self.send_token_to_the_left()
        self.wait_for_token()
        #the players just draw their first card. Broadcast own card.
        self.send_croupier_card()

        #send token and wait till it returns
        self.send_token_to_the_left()
        self.wait_for_token()
        #draw rest of cards
        self.draw_more_cards()
        #broadcast own result
        #receive answers from player
        self.retrieve_results()

        #write statistics
        self.write_statistics()

        #broadcast final results == end of round
        self.declare_end_of_round()

    def process_received_message(self, connection, message):
        if message.getAction() == "result?":
            amounts = self.count_cards()
            self.final_result = self.nearest_to_21(amounts)
            result_answer = "looser"
            if message.getMessage() < self.final_result <= 21:
                result_answer = "winner"
            elif message.getMessage() == self.final_result <= 21:
                result_answer = "tie"
            result_message = Message("result", result_answer,
                                     sender=self._ID + ":" + str(self.final_result) + ":" + str(self.role[0]))
            self.send_message_over_socket(connection, result_message)
        elif message.getAction() == "end":
            self.end_of_round = True
        elif message.getAction() == "croupier_card":
            self.croupier_card = message.getMessage()

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
        Er sendet seine order an alle und erhaelt als Antwort die order von allen anderen.
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

        self.order_of_all = self.order_of_players[:]
        self.croupier_id = self.order_of_players.pop(0)
        self.logger.info("ID of croupier: " + str(self.croupier_id))

        if self.croupier_id == self._ID:
            self.role = self.CROUPIER
        else:
            self.choose_role(my_order)

        # Warte auf den Token ehe mit dem Austeilen der Karten begonnen werden kann
        if self.token and self.croupier_id == self._ID:
            pass
        elif self.token:
            token_message = Message("token", "", sender=self._ID)
            self.send_message_to_id(token_message, self.croupier_id)
            self.token = False
        elif self.croupier_id == self._ID:
            self.wait_for_token()

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

    def draw_single_card(self):
        number = self._system_random.choice(self.CARDS)
        self.logger.info("My drawn card is: " + str(number))
        self.own_cards.append(number)
        self.logger.info("My hand is now: " + str(self.own_cards))

    def draw_more_cards(self):
        hit = self.do_i_want_a_new_card()
        while hit:
            self.draw_single_card()
            hit = self.do_i_want_a_new_card()

    def do_i_want_a_new_card(self):
        if self.role == self.CROUPIER:
            amount = self.count_croupier_cards()
            if amount < 17:
                return True
            else:
                return False
        elif self.role == self.SAFE:
            return self.choose_it_safely()
        else:
            amounts = self.count_cards()
            if min(amounts) > 16:
                return False
            elif min(amounts) <= 16:
                return True

    def choose_it_safely(self):
        '''
        return True = Hit
        return False = Stay
        Sollte mit ner coolen Matrix irgendwie programmiert werden. Aber das hier soll erst mal reichen.
        '''
        amounts = self.count_cards()
        # obviously
        if 21 in amounts:
            return False

        # soft hand
        if 11 in self.own_cards and len(self.own_cards) == 2:
            # hat der Spieler eine 2, 3, 4, 5 oder 6 auf der Hand?
            if any(number in self.own_cards for number in [2, 3, 4, 5, 6]):
                return True
            elif 7 in self.own_cards:
                if self.croupier_card <= 8:
                    return False
                else:
                    return True
            elif any(number in self.own_cards for number in [8, 9]):
                return False

        #hard hand
        if min(amounts) < 11:
            return True
        elif min(amounts) == 12:
            if self.croupier_card <= 3 or self.croupier_card >= 7:
                return True
            else:
                return False
        elif min(amounts) <= 16:
            if self.croupier_card <= 6:
                return False
            else:
                return True
        else:  # 17-20
            return False

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
        result_message = Message("result?", self.final_result)
        self.results = {}
        for ID in self.order_of_players:
            socket = self.send_message_to_id(result_message, ID)
            answer = self.receive_message_from_socket(socket)
            if answer.getMessage() in self.results:
                self.results[answer.getMessage()] += [answer.getSender()]
            else:
                self.results[answer.getMessage()] = [answer.getSender()]

    def send_croupier_card(self):
        croupier_card_message = Message("croupier_card", self.own_cards[0], sender=self._ID)
        for ID in self.order_of_players:
            self.send_message_to_id(croupier_card_message, ID)

    def declare_end_of_round(self):
        self.end_of_round = True
        self.results["croupier"] = self._ID + ":" + str(self.final_result)
        end_message = Message("end", self.results, sender=self._ID)
        for ID in self.order_of_players:
            self.send_message_to_id(end_message, ID)

    def send_token_to_the_left(self):
        token_message = Message("token", "", sender=self._ID)
        # gib die ID aus, die links von einem steht. Bei der letzten ID nimm die erste.
        left_neighbour_id = self.order_of_all[
            (self.order_of_all.index(self._ID) + 1) % len(self.order_of_all)]
        self.send_message_to_id(token_message, left_neighbour_id)
        self.token = False

    def wait_for_token(self):
        socket, received_message = self.return_received_message()
        if received_message.getAction() == "token":
            self.token = True
        else:
            self.logger.fatal("WTF are you sending?? I am actually waiting for the token.")
            sys.exit(1)

    def write_statistics(self):
        self.logger.info("writing statistics")
        # are there any winners?
        if "winner" not in self.results:
            self.read_stat_file_and_raise_its_value("wins_croupier", 1)
        else:
            safe_wins = 0
            risk_wins = 0
            for winner in self.results["winner"]:
                if "s" in winner:
                    safe_wins += 1
                elif "r" in winner:
                    risk_wins += 1
            self.read_stat_file_and_raise_its_value("wins_safe", safe_wins)
            self.read_stat_file_and_raise_its_value("wins_risk", risk_wins)

    @staticmethod
    def read_stat_file_and_raise_its_value(filename, raise_by):
        with open("./Logging/" + filename, "r+") as stat_file:
            amount_winners = int(stat_file.read())
            amount_winners += raise_by
            stat_file.seek(0)
            stat_file.write(str(amount_winners))


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
