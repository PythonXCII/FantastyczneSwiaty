from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from operator import attrgetter
from kivy.uix.popup import Popup


class WyspaPopup(Popup):
    list_of_cards = ListProperty()

    def __init__(self, list_of_cards, **kwargs):
        super(WyspaPopup, self).__init__(**kwargs)
        self.list_of_cards = list_of_cards

    def use(self, element):
        card = self.list_of_cards[-1]
        card.extra_ability = element
        card.name_to_display = "Wyspa + {}".format(element)
        self.dismiss()


class MimikPopup(Popup):
    list_of_cards = ListProperty()

    def __init__(self, list_of_cards, **kwargs):
        super(MimikPopup, self).__init__(**kwargs)
        self.list_of_cards = list_of_cards

    def use(self, element):
        card = self.list_of_cards[-1]
        card.name = element.name
        card.power = element.power
        card.set = element.set
        card.name_to_display = "Mimik + {}".format(element.name)
        if hasattr(element, "penalty"):
            card.card_points = element.penalty
        self.dismiss()
        return


class KsiegaZmianSetPopup(Popup):
    element = ObjectProperty()
    card = ObjectProperty()

    def __init__(self, element, card, **kwargs):
        super(KsiegaZmianSetPopup, self).__init__(**kwargs)
        self.element = element
        self.card = card

    def use(self, card_set):
        self.element.set = card_set
        self.card.name_to_display = "Księga Zmian + {} + {}".format(self.element.name, self.element.set)
        self.dismiss()


class KsiegaZmianPopup(MimikPopup):
    def use(self, element, ):
        KsiegaZmianSetPopup(element, self.list_of_cards[-1]).open()
        self.dismiss()


class SelectCardWindow(Widget):
    list_of_cards = ListProperty()
    count_cards = StringProperty()
    sum_to_display = StringProperty()

    class KrasnoludzkaPiechota:
        name = "Krasnoludzka Piechota"
        name_to_display = name
        canceled_card = False
        power = 15
        set = "Armia"
        description = "KARA: -2 za każdą inną kartę Armii."

        def penalty(self, list_of_cards):
            if any(card.name in ("Zwiadowcy", "Runa ochrony") for card in list_of_cards):
                return self.power
            else:
                penalty = 0
                for card in list_of_cards:
                    if card.set == "Armia" and not card.canceled_card and card != self:
                        penalty += 2
                return self.power - penalty

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class ElfiLucznicy:
        name = "Elfi łucznicy"
        name_to_display = name
        canceled_card = False
        power = 10
        set = "Armia"
        description = "PREMIA: +5, jeśli nie masz żadnej karty Pogody."

        def card_points(self, list_of_cards):
            for card in list_of_cards:
                if card.set == "Pogoda" and not card.canceled_card:
                    return self.power
            return self.power + 5

    class Rycerze:
        name = "Rycerze"
        name_to_display = name
        canceled_card = False
        power = 20
        set = "Armia"
        description = "KARA: -8, chyba że masz przynajmniej 1 kartę Przywódcy"

        def penalty(self, list_of_cards):
            if any((card.set == "Przywódca" or card.name == "Runa ochrony") and not card.canceled_card
                   for card in list_of_cards):
                return self.power
            return self.power - 8

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class LekkaKonnica:
        name = "Lekka konnica"
        name_to_display = name
        canceled_card = False
        power = 17
        set = "Armia"
        description = "KARA: -2 za każdą kartę Krainy."

        def penalty(self, list_of_cards):
            penalty = 0
            if not any(card.name == "Runa ochrony" for card in list_of_cards):
                for card in list_of_cards:
                    if card.set == "Kraina" and not card.canceled_card:
                        penalty += 2
            return self.power - penalty

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class Zwiadowcy:
        name = "Zwiadowcy"
        name_to_display = name
        canceled_card = False
        power = 5
        set = "Armia"
        description = "PREMIA: +10 za każdą kartę Krainy. USUWA słowo Armia z kar wszystkich kart."

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set == "Kraina" and not card.canceled_card:
                    bonus += 10
            return self.power + bonus

    class Bazyliszek:
        name = "Bazyliszek"
        name_to_display = name
        canceled_card = False
        power = 35
        set = "Bestia"
        description = "KARA: ANULUJE wszystkie karty Armii, Przywódcy i innych Bestii."

        def penalty(self, list_of_cards):
            if not any(card.name in ("Władca bestii", "Runa ochrony") for card in list_of_cards):
                for card in list_of_cards:
                    if card.set == "Armia" and not any(card.name == "Zwiadowcy" for card in list_of_cards):
                        card.canceled_card = True
                    if card.set == "Przywódca" or (card.set == "Bestia" and card != self):
                        card.canceled_card = True
            if any(card.name_to_display == "Mimik + Bazyliszek" for card in list_of_cards):
                self.canceled_card = True

            return self.power

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class Smok:
        name = "Smok"
        name_to_display = name
        canceled_card = False
        power = 30
        set = "Bestia"
        description = "KARA: -40, chyba że masz przynajmniej 1 kartę Czarodzieja"

        def penalty(self, list_of_cards):
            if not any(card.set == "Czarodziej" and not card.canceled_card for card in list_of_cards):
                if not any(card.name in ("Władca bestii", "Runa ochrony") for card in list_of_cards):
                    return self.power - 40
            return self.power

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class Hydra:
        name = "Hydra"
        name_to_display = name
        canceled_card = False
        power = 12
        set = "Bestia"
        description = "PREMIA: +28 z Bagnem."

        def card_points(self, list_of_cards):
            if any(card.name == "Bagno" for card in list_of_cards):
                return self.power + 28
            return self.power

    class Jednorozec:
        name = "Jednorożec"
        name_to_display = name
        canceled_card = False
        power = 9
        set = "Bestia"
        description = "PREMIA: +30 z Księżniczką ALBO +15 z Cesarzową, Królową albo Zaklinaczką."

        def card_points(self, list_of_cards):
            if any(card.name == "Księżniczka" for card in list_of_cards):
                return self.power + 30
            if any(card.name in ("Cesarzowa", "Królowa", "Zaklinaczka") for card in list_of_cards):
                return self.power + 15
            return self.power

    class Rumak:
        name = "Rumak"
        name_to_display = name
        canceled_card = False
        power = 6
        set = "Bestia"
        description = "PREMIA: +14 z dowolną kartą Przywódcy albo Czarodzieja."

        def card_points(self, list_of_cards):
            if any(card.set in ("Przywódca", "Czarodziej") for card in list_of_cards):
                return self.power + 14
            return self.power

    class Swieca:
        name = "Świeca"
        name_to_display = name
        canceled_card = False
        power = 2
        set = "Płomień"
        description = "PREMIA: +100 z Księgą zmian, Dzwonnicą i dowolną kartą Czarodzieja."

        def card_points(self, list_of_cards):
            if any(card.set == "Czarodziej" for card in list_of_cards):
                if any(card.name == "Księga zmian" for card in list_of_cards):
                    if any(card.set == "Dzwonnica" for card in list_of_cards):
                        return self.power + 100
            return self.power

    class ZywiolakOgnia:
        name = "Żywiołak ognia"
        name_to_display = name
        canceled_card = False
        power = 4
        set = "Płomień"
        description = "PREMIA: +15 za każdą inną kartę Płomienia."

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set == self.set and card != self:
                    bonus += 15
            return self.power + bonus

    class Kuznia:
        name = "Kuźnia"
        name_to_display = name
        canceled_card = False
        power = 9
        set = "Płomień"
        description = "PREMIA: +9 za każdą kartę Broni i Artefaktu."

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set in ("Broń", "Artefakt"):
                    bonus += 9
            return self.power + bonus

    class Blyskawica:
        name = "Błyskawica"
        name_to_display = name
        canceled_card = False
        power = 11
        set = "Płomień"
        description = "PREMIA: +30 z Burzą"

        def card_points(self, list_of_cards):
            if any(card.name == "Burza" for card in list_of_cards):
                return self.power + 30
            return self.power

    class Pozar:
        name = "Pożar"
        name_to_display = name
        canceled_card = False
        power = 40
        set = "Płomień"
        description = "KARA: ANULUJE wszystkie karty z wyjątkiem Płomienia, Czarodzieja, " \
                      "Pogody, Broni, Artefaktu, Gór, Potopu, Wyspy, Jednorożca i Smoka"

        def penalty(self, list_of_cards):
            if not any(card.name == "Runa ochrony" for card in list_of_cards):
                if not any(card.name == "Wyspa" and card.extra_ability == self.name and not card.canceled_card
                           for card in list_of_cards):
                    for card in list_of_cards:
                        if not card.set in ("Płomień", "Czarodziej", "Pogoda", "Broń", "Artefakt"):
                            if not card.name in ("Góry", "Potop", "Wyspa", "Jednorożec", "Smok"):
                                card.canceled_card = True
            return self.power

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class FontannaZycia:
        name = "Fontanna życia"
        name_to_display = name
        canceled_card = False
        power = 1
        set = "Powódź"
        description = "PREMIA: Dodaj podstawową siłę dowolnej karty Broni, " \
                      "Powodzi, Płomienia, Krainy albo Pogody w ręce"

        def card_points(self, list_of_cards):
            list_of_points = []
            for card in list_of_cards:
                if card.set in ("Broń", "Powódź", "Płomień", "Kraina", "Pogoda") and not card.canceled_card:
                    list_of_points.append(card.power)
            if list_of_points == []:
                return self.power
            else:
                return self.power + max(list_of_points)

    class Potop:
        name = "Potop"
        name_to_display = name
        canceled_card = False
        power = 32
        set = "Powódź"
        description = "KARA: ANULUJE wszystkie karty Armii, wszystkie karty Krainy z wyjątkiem Gór " \
                      "i wszystkie karty Płomienia z wyjątkiem Błyskawicy."

        def penalty(self, list_of_cards):
            if not any(card.name in ("Runa ochrony", "Góry", "Zwiadowcy") and not card.canceled_card
                       for card in list_of_cards):
                if not any(card.name == "Wyspa" and card.extra_ability == self.name and not card.canceled_card
                           for card in list_of_cards):
                    for card in list_of_cards:
                        if card.set == "Armia" and not any(card.name == "Okręt" and not card.canceled_card
                                                           for card in list_of_cards):
                            card.canceled_card = True
                        if card.set in ("Kraina", "Płomień"):
                            if card.name not in ("Góry", "Błyskawica"):
                                card.canceled_card = True
            return self.power

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class Wyspa:
        name = "Wyspa"
        name_to_display = name
        canceled_card = False
        power = 14
        set = "Powódź"
        description = "PREMIA: USUWA karę z dowolnej karty Powodzi albo Płomienia"
        extra_ability = ""

        def ability(self, list_of_cards):
            if self.extra_ability == "":
                WyspaPopup(list_of_cards).open()

        def card_points(self, list_of_cards):
            return self.power

    class Bagno:
        name = "Bagno"
        name_to_display = name
        canceled_card = False
        power = 18
        set = "Powódź"
        description = "KARA: -3 za każdą kartę Armii i Płomienia"

        def penalty(self, list_of_cards):
            penalty = 0
            if not any(card.name in ("Runa ochrony", "Góry") and not card.canceled_card for card in list_of_cards):
                if not any(card.name == "Wyspa" and card.extra_ability == self.name and not card.canceled_card
                           for card in list_of_cards):
                    for card in list_of_cards:
                        if card.set == "Armia" and not any(card.name == "Okręt" for card in list_of_cards):
                            penalty += 3
                        if card.set == "Płomień":
                            penalty += 3
                return self.power - penalty

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class ZywiolakWody:
        name = "Żywiołak wody"
        name_to_display = name
        canceled_card = False
        power = 4
        set = "Powódź"
        description = "PREMIA: +15 za każdą inną kartę Powodzi."

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set == self.set and card != self:
                    bonus += 15
            return self.power + bonus

    class Dzwonnica:
        name = "Dzwonnica"
        name_to_display = name
        canceled_card = False
        power = 8
        set = "Kraina"
        description = "PREMIA: +15 z dowolną kartą Czarodzieja."

        def card_points(self, list_of_cards):
            if any(card.set == "Czarodziej" and not card.canceled_card for card in list_of_cards):
                return self.power + 15
            return self.power

    class Jaskinia:
        name = "Jaskinia"
        name_to_display = name
        canceled_card = False
        power = 6
        set = "Kraina"
        description = "PREMIA: +25 z Krasnoludzką piechotą lub Smokiem. USUWA kary wszystkiech kart Pogody."

        def card_points(self, list_of_cards):
            if any(card.name in ("Krasnoludzka piechota", "Smok") and not card.canceled_card for card in list_of_cards):
                return self.power + 25
            return self.power

    class ZywiolakZiemi:
        name = "Żywiołak ziemi"
        name_to_display = name
        canceled_card = False
        power = 4
        set = "Kraina"
        description = "PREMIA: +15 za każdą inną kartę Krainy."

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set == self.set and card != self and not card.canceled_card:
                    bonus += 15
            return self.power + bonus

    class Las:
        name = "Las"
        name_to_display = name
        canceled_card = False
        power = 7
        set = "Kraina"
        description = "PREMIA: +12 za każdą kartę Bestii i Elfich łuczników"

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if (card.set == "Bestia" or card.name == "Elfi łucznicy") and not card.canceled_card:
                    bonus += 12
            return self.power + bonus

    class Gory:
        name = "Góry"
        name_to_display = name
        canceled_card = False
        power = 9
        set = "Kraina"
        description = "PREMIA: +50 z Dymem i Pożarem. USUWA kary z wszystkich kart Powodzi."

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if (card.set == "Bestia" or card.name == "Elfi łucznicy") and not card.canceled_card:
                    bonus += 12
            return self.power + bonus

    class Cesarzowa:
        name = "Cesarzowa"
        name_to_display = name
        canceled_card = False
        power = 15
        set = "Przywódca"
        description = "PREMIA: +10 za każdą kartę Armii. KARA: -5 za każdą inną kartę Przywódcy."

        def card_points(self, list_of_cards):
            bonus, penalty = 0, 0
            for card in list_of_cards:
                if card.set == "Armia" and not card.canceled_card:
                    bonus += 10
                if not any(card.name == "Runa ochrony" for card in list_of_cards):
                    if card.set == self.set and card != self and not card.canceled_card:
                        penalty += 5
            return self.power + bonus - penalty

    class Krol:
        name = "Król"
        name_to_display = name
        canceled_card = False
        power = 8
        set = "Przywódca"
        description = "PREMIA: +5 za każdą kartę Armii. ALBO +20 za każdą kartę Armii, jeśli masz Królową"

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if any(card.name == "Królowa" and not card.canceled_card for card in list_of_cards):
                    if card.set == "Armia" and not card.canceled_card:
                        bonus += 20
                else:
                    if card.set== "Armia" and not card.canceled_card:
                        bonus += 5
            return self.power + bonus

    class Ksiezniczka:
        name = "Księżniczka"
        name_to_display = name
        canceled_card = False
        power = 2
        set = "Przywódca"
        description = "PREMIA: +8 za każdą kartę Armii, Czarodzieja i innego Przywódcy"

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set in ("Armia", "Czarodziej", "Przywódca") and card != self \
                        and not card.canceled_card:
                    bonus += 8
            return self.power + bonus

    class Krolowa:
        name = "Królowa"
        name_to_display = name
        canceled_card = False
        power = 6
        set = "Przywódca"
        description = "PREMIA: +5 za każdą kartę Armii. ALBO +20 za każdą kartę Armii, jeśli masz Króla"

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if any(card.name == "Król" and not card.canceled_card for card in list_of_cards):
                    if card.set == "Armia" and not card.canceled_card:
                        bonus += 20
                else:
                    if card.set == "Armia" and not card.canceled_card:
                        bonus += 5
            return self.power + bonus

    class WielkiWodz:
        name = "Wielki wódz"
        name_to_display = name
        canceled_card = False
        power = 4
        set = "Przywódca"
        description = "PREMIA: Suma podstawowych wartości siły wszystkich kart Armii."

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set == "Armia" and not card.canceled_card:
                    bonus += card.power
            return self.power + bonus

    class ElfiDlugiLuk:
        name = "Elfi długi łuk"
        name_to_display = name
        canceled_card = False
        power = 3
        set = "Broń"
        description = "PREMIA: +30 z Elfimi łucznikami, Wielkim wodzem albo Władcą bestii."

        def card_points(self, list_of_cards):
            if any(card.name in ("Elfi łucznicy", "Wielki wódz", "Władca bestii") and
                   not card.canceled_card for card in list_of_cards):
                return self.power + 30
            return self.power

    class MagicznaRozdzka:
        name = "Magiczna różdżka"
        name_to_display = name
        canceled_card = False
        power = 1
        set = "Broń"
        description = "PREMIA: +25 z dowolną kartą Czarodzieja."

        def card_points(self, list_of_cards):
            if any(card.set == "Czarodziej" and not card.canceled_card for card in list_of_cards):
                return self.power + 25
            return self.power

    class MieczKetha:
        name = "Miecz Ketha"
        name_to_display = name
        canceled_card = False
        power = 7
        set = "Broń"
        description = "PREMIA: +10 z dowolną kartą Przywódcy ALBO +40 z dowolną kartą Przywódcy i Tarczą Ketha."

        def card_points(self, list_of_cards):
            if any(card.set == "Przywódca" and not card.canceled_card for card in list_of_cards):
                if any(card.name == "Tarcza Ketha" and not card.canceled_card for card in list_of_cards):
                    return self.power + 40
                else:
                    return self.power + 10
            return self.power

    class SterowiecWojenny:
        name = "Sterowiec wojenny"
        name_to_display = name
        canceled_card = False
        power = 35
        set = "Broń"
        description = "KARA: ANULOWANY, chyba że masz przynajmniej 1 kartę Armii. ANULOWANY z dowolną kasrtą pogody."

        def penalty(self, list_of_cards):
            if not any(card.name == "Runa ochrony" for card in list_of_cards):
                if not any(card.name == "Zwiadowcy" and not card.canceled_card for card in list_of_cards):
                    if not any(card.set == "Armia" for card in list_of_cards):
                        self.canceled_card = True
                if any(card.set == "Pogoda" for card in list_of_cards):
                    self.canceled_card = True
            return self.power

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class Okret:
        name = "Okręt"
        name_to_display = name
        canceled_card = False
        power = 23
        set = "Broń"
        description = "KARA: ANULOWANY, chyba że masz przynajmniej 1 kartę Powodzi. " \
                      "USUWA słowo Armia z wszystkich kar wszystkich kart powodzi."

        def penalty(self, list_of_cards):
            if not any((card.set == "Powódź" or card.name == "Runa ochrony") and not card.canceled_card
                       for card in list_of_cards):
                self.canceled_card = True
            return self.power

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class ZywiolakPowietrza:
        name = "Żywiołak powietrza"
        name_to_display = name
        canceled_card = False
        power = 4
        set = "Pogoda"
        description = "PREMIA: +15 za każdą inną kartę Pogody."

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set == self.set and card != self and not card.canceled_card:
                    bonus += 15
            return self.power + bonus

    class Sniezyca:
        name = "Śnieżyca"
        name_to_display = name
        canceled_card = False
        power = 30
        set = "Pogoda"
        description = "KARA: ANULUJE wszystkie karty Powodzi. -5 za każdą kartę Armii, Przywódcy, Bestii i Płomienia."

        def penalty(self, list_of_cards):
            penalty = 0
            if not any(card.name in ("Runa ochrony", "Jaskinia") and not card.canceled_card for card in list_of_cards):
                for card in list_of_cards:
                    if card.set == "Powódź":
                        card.canceled_card = True
                    if card.set in ("Przywódca", "Bestia", "Płomień") and not card.canceled_card:
                        penalty += 5
                    if not any(card.name == "Zwiadowcy" and not card.canceled_card for card in list_of_cards):
                        if card.set == "Armia" and not card.canceled_card:
                            penalty += 5
            return self.power - penalty

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class Burza:
        name = "Burza"
        name_to_display = name
        canceled_card = False
        power = 8
        set = "Pogoda"
        description = "PREMIA: +10 za każdą kartę Powodzi. KARA: " \
                      "ANULUJE wszystkie karty Płomienia z wyjątkiem Błyskawicy"

        def penalty(self, list_of_cards):
            if not any(card.name in ("Runa ochrony", "Jaskinia") and not card.canceled_card for card in list_of_cards):
                for card in list_of_cards:
                    if card.set == "Płomień" and card.name != "Błyskawica":
                        card.canceled_card = True

        def card_points(self, list_of_cards):
            self.penalty(list_of_cards)
            bonus = 0
            for card in list_of_cards:
                if card.set == "Powódź" and not card.canceled_card:
                    bonus += 10
            return self.power + bonus

    class Dym:
        name = "Dym"
        name_to_display = name
        canceled_card = False
        power = 27
        set = "Pogoda"
        description = "KARA: Ta kara zostaje ANULOWANA, chyba że masz przynajmniej 1 kartę Płomienia"

        def penalty(self, list_of_cards):
            if not any((card.name in ("Runa ochrony", "Jaskinia") or card.set == "Płomień")
                       and not card.canceled_card for card in list_of_cards):
                self.canceled_card = True
            return self.power

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class Tornado:
        name = "Tornado"
        name_to_display = name
        canceled_card = False
        power = 13
        set = "Pogoda"
        description = "PREMIA: +40 z Burzą i Śnieżycą albo Burzą i Potopem"

        def card_points(self, list_of_cards):
            if any(card.name == "Burza" and not card.canceled_card for card in list_of_cards):
                if any(card.name in ("Śnieżyca", "Potop") and not card.canceled_card for card in list_of_cards):
                    return self.power + 40
            return self.power

    class KsiegaZmian:
        name = "Księga zmian"
        name_to_display = name
        canceled_card = False
        power = 3
        set = "Artefakt"
        description = "PREMIA: Możesz zmienić zestaw do którego należy 1 inna karta. " \
                      "Jej nazwa, premia i kary pozostają te same."
        extra_ability = ""

        def ability(self, list_of_cards):
            KsiegaZmianPopup(list_of_cards).open()

        def card_points(self, list_of_cards):
            return self.power

    class TarczaKetha:
        name = "Tarcza Ketha"
        name_to_display = name
        canceled_card = False
        power = 4
        set = "Artefakt"
        description = "PREMIA: +15 z dowolną kartą Przywódcy ALBO +40 z dowolną kartą Przywódcy i Mieczem Ketha."

        def card_points(self, list_of_cards):
            if any(card.set == "Przywódca" and not card.canceled_card for card in list_of_cards):
                if any(card.name == "Miecz Ketha" and not card.canceled_card for card in list_of_cards):
                    return self.power + 40
                else:
                    return self.power + 15
            return self.power

    class KlejnotPorzadku:
        name = "Klejnot porządku"
        name_to_display = name
        canceled_card = False
        power = 5
        set = "Artefakt"
        description = "PREMIA: Odnosi się do podstawowej wartości siły, +10 za 3 karty pod rząd itd."

        def card_points(self, list_of_cards):
            score = []
            count = 1
            sorted_list = []
            for card in list_of_cards:
                if not card.canceled_card:
                    sorted_list.append(card)
            sorted_list = sorted(sorted_list, key=attrgetter("power"))
            try:
                for i in range(9):
                    if sorted_list[i+1].power - sorted_list[i].power == 1:
                        count += 1
                    elif sorted_list[i+1].power - sorted_list[i].power == 0:
                        pass
                    else:
                        score.append(count)
                        count = 1
            except IndexError:
                pass
            if max(score) == 3:
                return self.power + 10
            elif max(score) == 4:
                return self.power + 30
            elif max(score) == 5:
                return self.power + 60
            elif max(score) == 6:
                return self.power + 100
            elif max(score) == 7:
                return self.power + 150
            else:
                return self.power

    class DrzewoSwiata:
        name = "Drzewo świata"
        name_to_display = name
        canceled_card = False
        power = 2
        set = "Artefakt"
        description = "PREMIA: +50, jeśli każda nie-ANULOWANA karta pochodzi z innego zestawu."

        def card_points(self, list_of_cards):
            sorted_list = []
            for card in list_of_cards:
                if not card.canceled_card:
                    sorted_list.append(card)
            sorted_list = sorted(sorted_list, key=attrgetter("set"))
            try:
                for i in range(9):
                    if sorted_list[i+1].set == sorted_list[i].set:
                        return self.power
            except IndexError:
                pass
            return self.power + 50

    class RunaOchrony:
        name = "Runa ochrony"
        name_to_display = name
        canceled_card = False
        power = 1
        set = "Artefakt"
        description = "PREMIA: USUWA kary z wszystkich kart."

        def card_points(self, list_of_cards):
            return self.power

    class WladcaBestii:
        name = "Władca bestii"
        name_to_display = name
        canceled_card = False
        power = 9
        set = "Czarodziej"
        description = "PREMIA: +9 za każdą kartę Bestii. USUWA kary z wszystkich kart Bestii."

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set == "Bestia" and not card.canceled_card:
                    bonus += 9
            return self.power + bonus

    class Kolekcjoner:
        name = "Kolekcjoner"
        name_to_display = name
        canceled_card = False
        power = 7
        set = "Czarodziej"
        description = "PREMIA: +9 za każdą kartę Bestii. USUWA kary z wszystkich kart Bestii."

        def card_points(self, list_of_cards):
            score = []
            count = 1
            sorted_list = []
            for card in list_of_cards:
                if not card.canceled_card:
                    sorted_list.append(card)
            sorted_list = sorted(sorted_list, key=attrgetter("set"))
            try:
                for i in range(9):
                    if sorted_list[i + 1].set == sorted_list[i].set:
                        count += 1
                    else:
                        score.append(count)
                        count = 1
            except IndexError:
                pass
            if max(score) == 3:
                return self.power + 10
            elif max(score) == 4:
                return self.power + 40
            elif max(score) == 5:
                return self.power + 100
            else:
                return self.power

    class Zaklinaczka:
        name = "Zaklinaczka"
        name_to_display = name
        canceled_card = False
        power = 5
        set = "Czarodziej"
        description = "PREMIA: +5 za każdą kartę Krainy, Pogody, Powodzi i Płomienia"

        def card_points(self, list_of_cards):
            bonus = 0
            for card in list_of_cards:
                if card.set in ("Kraina", "Pogoda", "Powódź", "Płomień") and not card.canceled_card:
                    bonus += 5
            return self.power + bonus

    class Nekromanta:
        name = "Nekromanta"
        name_to_display = name
        canceled_card = False
        power = 3
        set = "Czarodziej"
        description = "PREMIA: Na koniec gry możesz wziąć z obszaru kart odrzuconych 1 kartę Armii, Przywódcy, " \
                      "Czarodzieja albo Bestii i dołączyć ją do swoich kart na ręce jako ósmą kartę."

        def card_points(self, list_of_cards):
            return self.power

    class Czarnoksieznik:
        name = "Czarnoksiężnik"
        name_to_display = name
        canceled_card = False
        power = 25
        set = "Czarodziej"
        description = "KARA: -10 za każdą kartę Przywódcy i każdą inną kartę Czarodzieja."

        def penalty(self, list_of_cards):
            penalty = 0
            if not any(card.name == "Runa ochrony" for card in list_of_cards):
                for card in list_of_cards:
                    if card.set in ("Przywódca", "Czarodziej") and not card.canceled_card and card != self:
                        penalty += 10
            return self.power - penalty

        def card_points(self, list_of_cards):
            return self.penalty(list_of_cards)

    class Blazen:
        name = "Błazen"
        name_to_display = name
        canceled_card = False
        power = 3
        set = "Czarodziej"
        description = "PREMIA: +3 za każdą inną kartę posiadającą nieparzystą podstawową siłę " \
                      "ALBO +50, jeśli każda karta na Twojej ręce posiada nieparzystą podstawową siłę."

        def card_points(self, list_of_cards):
            bonus = 0
            if all(card.power % 2 == 1 for card in list_of_cards):
                return self.power + 50
            sorted_list = []
            for card in list_of_cards:
                if not card.canceled_card:
                    sorted_list.append(card)
            sorted_list = sorted(sorted_list, key=attrgetter("name"))
            try:
                for i in range(9):
                    if sorted_list[i + 1].name != sorted_list[i].name and sorted_list[i].power % 2 == 1:
                        bonus += 3
            except IndexError:
                pass
            return self.power + bonus

    class Mimik:
        name = "Mimik"
        name_to_display = name
        canceled_card = False
        power = 0
        set = "Specjalne"
        description = "Może zduplikować nazwę, podstawową siłę, zestaw i karę, " \
                      "ALE NIE PREMIĘ dowolnej innej karty z Twojej ręki"
        extra_ability = ""

        def ability(self, list_of_cards):
            MimikPopup(list_of_cards).open()

        def card_points(self, list_of_cards):
            return self.power

    class Fatamorgana:
        name = "Fatamorgana"
        canceled_card = False
        power = 0
        set = "Specjalne"
        description = "Może zduplikować nazwę i zestaw, do którego należy dowolna karta ..."
        extra_ability = ""

        def ability(self, list_of_cards):
            WyspaPopup(list_of_cards).open()

        def card_points(self, list_of_cards):
            return self.power

    class Zmiennoksztaltny:
        name = "Zmiennokształtny"
        canceled_card = False
        power = 0
        set = "Specjalne"
        description = "Może zduplikować nazwę i zestaw, do którego należy dowolna karta ..."
        extra_ability = ""

        def ability(self, list_of_cards):
            if self.extra_ability == "":
                WyspaPopup(list_of_cards).open()

        def card_points(self, list_of_cards):
            return self.power

    class EmptyCard:
        name = ""
        name_to_display = name
        canceled_card = False
        power = 0
        set = ""
        description = ""

        def card_points(self, list_of_cards):
            pass

    def count_cards_function(self):
        i = "8" if any(isinstance(card, self.Nekromanta) and not card.canceled_card
                       for card in self.list_of_cards) else "7"
        self.count_cards = "{}/{}".format(str(len(self.list_of_cards)), i)

    def add_card(self, card):
        i = 8 if any(isinstance(element, self.Nekromanta) and not element.canceled_card
                     for element in self.list_of_cards) else 7
        if len(self.list_of_cards) < i:
            if not any(element.name == card.name for element in self.list_of_cards):
                self.list_of_cards.append(card())
                if hasattr(card, "ability"):
                    card.ability(card, self.list_of_cards)

        self.count_cards_function()
        self.sum_to_display = "0"

    def del_card(self, card):
        del self.list_of_cards[card]
        self.count_cards_function()
        self.sum_to_display = "0"

    def display_result(self):
        # adding EmptyCard and instant delete to refresh UI
        self.list_of_cards.append(self.EmptyCard())
        self.list_of_cards.pop()
        # double check because last cards in list can change firsts cards parameters
        self.points_sum()
        self.sum_to_display = str(self.points_sum())
        # reset properties
        for card in self.list_of_cards:
            card.canceled_card = False

    def points_sum(self):
        points_sum = 0
        for card in self.list_of_cards:
            if not card.canceled_card:
                points_sum += card.card_points(self.list_of_cards)
        return points_sum

    def reset(self):
        self.list_of_cards = []
        self.sum_to_display = "0"
        self.count_cards_function()


class MyApp(App):
    def build(self):
        return SelectCardWindow()


if __name__ == "__main__":
    MyApp().run()
