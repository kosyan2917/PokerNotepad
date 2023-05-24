from dataclasses import dataclass, asdict, field
import dacite
from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.pagelayout import PageLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


@dataclass
class Card:
    num: str
    suit: str

@dataclass
class Player:
    stack: int
    position: int
    hero: bool = False
    hand: list[Card] = field(default_factory=list)
    actions: list[list] = field(default_factory=lambda: [[],[],[],[]])

    def make_raise(self, street, bet):
        self.actions[street].append(f"Рейз {bet}")

    def make_call(self, street, bet):
        self.actions[street].append(f"Колл {bet}")

    def make_check(self, street):
        self.actions[street].append(f"Чек")

    def make_fold(self, street):
        self.actions[street].append(f"Выбросил")

    def make_allin(self, street):
        self.actions[street].append(f"Вабанк {self.stack}")

@dataclass
class Note:
    flop: list[Card]
    turn: Card
    river: Card
    hero: int
    players: list[Player]


players = [Player(100, 3), Player(20, 4)]
players[0].make_raise(0, 2)
players[1].make_raise(0, 6)
players[0].make_call(0,6)
players[0].make_check(1)
players[1].make_raise(1, 4)
players[0].make_check(2)
players[1].make_allin(2)
players[0].make_fold(2)






class Scroll(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_scroll_x = False
        self.do_scroll_y = True


class Filter(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"


class NewNote:

    def __init__(self, parent):
        self.cards = {'?': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8, '10': 9, 'J': 10, 'Q': 11,
                      'K': 12, 'A': 13}
        self.suits = ["spades", "clubs", "diamonds", "hearts"]
        self.parent = parent
        self.pages = [EnterBB, PlayerList, CardsPopup]
        self.actions = [self.to_player_list, self.to_the_game]
        self.players = []
        self._current_page = 0
        self.current_window = None
        self.blinds = self.enter_bb()

    @property
    def current_page(self):
        return self._current_page

    @current_page.setter
    def current_page(self, value):
        if value == -1:
            self.parent.to_main_page()
        else:
            self._current_page = value
            self.current_window = self.pages[value](to_prev_page=self.to_prev_page, to_next_page=self.to_next_page)
            self.parent.current_window = self.current_window

    def to_prev_page(self, *args):
        self.current_page = self.current_page - 1

    def to_next_page(self, *args):
        self.actions[self.current_page]()
        self.current_page = self.current_page + 1

    def enter_bb(self):
        self.bb = EnterBB(to_prev_page=self.to_prev_page, to_next_page=self.to_next_page)
        self.parent.current_window = self.bb
        self.current_window = self.bb

    def to_player_list(self):
        self.blinds = int(self.bb.bb.text)

    def to_the_game(self):
        self.players = []
        for player in self.current_window.list_of_players.children:
            hero = False
            if player.player_name == "Hero":
                hero = True
            card1 = player.card1.text.split(' ') #ToDO Доделать всю систему
            card2 = player.card2.text.split(' ')  # ToDO Доделать всю систему
            print(card1)
            stack = int(player.stack.text)/self.blinds
            pos = int(player.position.text)
            card1 = Card(*card1)
            card2 = Card(*card2)
            self.players.append(Player(stack=stack, position=pos, hero=hero, hand=[card1, card2]))


class EnterBB(BoxLayout):
    to_next_page = ObjectProperty()
    to_prev_page = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        bb_box = BoxLayout()
        bb_box.add_widget(Label(text='Блайнды'))
        self.al = AnchorLayout(anchor_x='center', anchor_y='center')
        self.bb = TextInput(multiline=False, size_hint=(0.8, 0.1))
        self.al.add_widget(self.bb)
        bb_box.add_widget(self.al)
        self.add_widget(bb_box)
        btns = BoxLayout(size_hint=(1,0.05))
        btns.add_widget(Button(text='Назад', on_release=self.to_prev_page))
        btns.add_widget(Button(text='Далее', on_release=self.to_next_page))
        self.add_widget(btns)


class NewPlayer(BoxLayout):
    player_name = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text=self.player_name))
        al = AnchorLayout(anchor_x='center', anchor_y='center')
        self.cards = BoxLayout()
        self.add_widget(al)
        self.card1 = Button(text='0 0', size_hint=(0.6, 0.6), on_release=self.change_card)
        self.card2 = Button(text='0 0', size_hint=(0.6, 0.6), on_release=self.change_card)
        self.cards.add_widget(self.card1)
        self.cards.add_widget(self.card2)
        al.add_widget(self.cards)
        al = AnchorLayout(anchor_x='center', anchor_y='center')
        self.stack = TextInput(multiline=False, size_hint=(0.8, 0.4))
        al.add_widget(self.stack)
        self.add_widget(al)
        self.position = Button(text="?", on_press=self.open_dd, size_hint=(0.6,0.2))
        self.add_widget(self.position)

    def change_card(self, *args):
        CardsPopup(source=args[0]).open()

    def open_dd(self, *args):
        dd = PosDropdown()
        print(dd.children[0].children)
        dd.open(args[0])


class PosDropdown(DropDown):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(1,9):
            btn = Button(text=f"{i}", size_hint=(None, None))
            btn.bind(on_release=self.select_option)
            self.add_widget(btn)

    def select_option(self, *args):
        self.select(args[0].text)
        self.attach_to.text = args[0].text



class PlayerList(BoxLayout):
    to_next_page = ObjectProperty()
    to_prev_page = ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.i=2
        print(self.to_next_page)
        self.orientation = "vertical"
        self.players = [NewPlayer(player_name="Hero"), NewPlayer(player_name="Player1")]
        self.list_of_players = BoxLayout(orientation="vertical")
        self.add_widget(self.list_of_players)
        btns = BoxLayout(size_hint=(1,0.3))
        add = Button(text="+", on_release=self.add_player, size_hint=(0.3, 0.4))
        remove = Button(text="-", on_release=self.remove_player, size_hint=(0.3, 0.4))
        btns.add_widget(add)
        btns.add_widget(remove)
        self.add_widget(btns)
        btns2 = BoxLayout(size_hint=(1, 0.4))
        self.add_widget(btns2)
        btns2.add_widget(Button(text='Назад',size_hint=(0.3, 0.4), on_release=self.to_prev_page))
        btns2.add_widget(Button(text='Далее',size_hint=(0.3, 0.4), on_release=self.to_next_page))
        for player in self.players:
            self.list_of_players.add_widget(player)

    def add_player(self, *args):
        player = NewPlayer(player_name=f"Player{self.i}")
        self.list_of_players.add_widget(player)
        self.players.append(player)
        # self.children[-1], self.children[-2] = self.children[-2], self.children[-1]
        self.i+=1

    def remove_player(self, *args):
        self.list_of_players.remove_widget(self.players[-1])
        self.players.pop(-1)
        self.i-=1


class Actions(BoxLayout):
    players = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Board)


class PlayersAction(BoxLayout):
    name = StringProperty()
    id = NumericProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        actions_bl = BoxLayout()
        self.add_widget(Label(text=self.name))
        self.add_widget(actions_bl)
        self.add_widget(Button(text='+',))

    def open_actions(self, *args):
        ActionsPopup().open()

class ActionsPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        bl = BoxLayout()
        self.add_widget(bl)
        
class Board(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Button(text='?', size_hint=(0.6, 0.6), on_release=self.change_card))
        self.add_widget(Button(text='?', size_hint=(0.6, 0.6), on_release=self.change_card))
        self.add_widget(Button(text='?', size_hint=(0.6, 0.6), on_release=self.change_card))
        self.add_widget(Button(text='?', size_hint=(0.6, 0.6), on_release=self.change_card))
        self.add_widget(Button(text='?', size_hint=(0.6, 0.6), on_release=self.change_card))


    def change_card(self, *args):
        CardsPopup(source=args[0]).open()


class CardButton(Button):
    value = StringProperty(None)
    suit = StringProperty(None)
    root = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        self.root.get_card(self.value, self.suit)


class CardsPopup(Popup):
    source = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards = {'?': 0, '2':1, '3':2, '4': 3, '5': 4, '6':5, '7':6, '8':7, '9':8, '10':9, 'J': 10, 'Q':11,
                      'K': 12, 'A':13}
        self.suits = ["spades", "clubs", "diamonds", "hearts"]
        self.pages = []
        self.pages_layout = PageLayout()
        self.add_widget(self.pages_layout)
        for suit in self.suits:
            root = BoxLayout(orientation="vertical")
            root.add_widget(Label(size_hint_y=0.1, text=suit))
            cards = GridLayout(rows=3, cols=5)
            for card in self.cards:
                cards.add_widget(CardButton(text=card, value=card, suit=suit, root=self))
            root.add_widget(cards)
            self.pages_layout.add_widget(root)

    def get_card(self, value, suit):
        print(value)
        if value == '?':
            self.source.text = '0 0'
        else:
            self.source.text=f"{value} {suit}"
        self.dismiss()

    def close(self):
        self.dismiss()


class MainPage(BoxLayout):

    callback = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Filter())
        self.add_widget(Scroll())
        float_layout = FloatLayout()
        print('Mainpage'+ str(self.callback))
        float_layout.add_widget(Button(size_hint=(0.2, 0.2), on_release=self.callback,
                                   pos_hint={'center_x': 0.5, 'y': 0.1}, text='Новая раздача',
                                   height=300))
        self.add_widget(float_layout)

    def call_back(self):
        self.callback()


class Notepad(BoxLayout):
    callback = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('Notepad' + str(self.callback))
        self.orientation = "vertical"
        self.current_widget = None

    def new_note(self):
        self.callback()


class PongApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_window = None

    @property
    def current_window(self):
        return self._current_window

    @current_window.setter
    def current_window(self, value):
        self._current_window = value
        if self.notepad.children:
            self.notepad.remove_widget(self.notepad.children[0])
        self.notepad.add_widget(value)

    def build(self):
        print('b')
        self.notepad = Notepad()
        self.to_main_page()
        return self.notepad

    def to_new_note(self, *args):
        newnote = NewNote(self)
        newnote.enter_bb()

    def to_main_page(self):
        self.current_window = MainPage(callback=self.to_new_note)

if __name__ == '__main__':

    PongApp().run()

