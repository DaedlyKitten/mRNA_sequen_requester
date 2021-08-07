
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import NumericProperty


# from kivy.uix.image import Image, AsyncImage
# from kivymd.uix.button import MDFlatButton


Builder.load_string(
'''

<constantSnack>:

    BoxLayout:
        id: box
        # height:self.minimum_height
        size_hint_y: root.sizeHint
        # height: dp(58)
        # size_hint_y: None
        height:lab.size[1]

        spacing: dp(5)
        padding: dp(10)
        y: -self.height

        canvas:
            Color:
                rgba: app.theme_cls.bg_normal
            Rectangle:
                pos: self.pos
                size: self.size

        MDLabel:
            id: lab
            size_hint_y: None
            multiline:True
            markup:True
            # adaptaive_height:True
            # height:self.text_size[1]
            # height: self.texture_size[1]
            # text_size: root.width, None
            # size: self.texture_size            
            font_size: root.font_size
            theme_text_color: 'Custom'
            text_color: app.theme_cls.text_color
            pos_hint: {'center_y': .5}
        # MDTextButton:
        #     text:'OK'
        #     on_press:root.hide()            

'''
)

class constantSnack(MDFloatLayout):
    font_size = NumericProperty("15sp")
    duration = NumericProperty(3)
    sizeHint=NumericProperty(0.06)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def add(self):
        Window.parent.add_widget(self) 
        self.showTimeLeft=-1

    def text(self,text='aaa',duration=3):
        self.ids.lab.text='[b]>  [/b]'+text
        if self.showTimeLeft<0:
            anim = Animation(y=0, d=0.2)
            anim.bind(on_complete=lambda *args: self.hideLater(duration))
            anim.start(self.ids.box)
            self.showTimeLeft=duration
        else: self.showTimeLeft=duration

    def hideLater(self,duration):
        self.checkEvent=Clock.schedule_interval(self.checkTime, 2)

    def checkTime(self,interval):
        self.showTimeLeft -= interval
        if self.showTimeLeft<0: self.hide()

    def hide(self):
        anim = Animation(y=-self.ids.box.height, d=0.2)
        anim.start(self.ids.box)
        Clock.unschedule(self.checkEvent)   

    # def on_touch_down(self, touch):
    #     print(touch.y)
    #     if touch.y<self.ids.box.height:
    #         # super(ModalView, self).on_touch_down(touch)
    #         # super().on_touch_down(touch)
            # self.showTimeLeft=-1
    #         self.hide()
    #         return True
    
            # return super().on_touch_down(touch)
        # if self.collide_point(touch.x, touch.y):

    # def dismiss(self):
    #     Window.parent.remove_widget(self)

    # def on_touch_down(self, touch):
    #     if self.duration <0:
    #         Window.parent.remove_widget(self)
