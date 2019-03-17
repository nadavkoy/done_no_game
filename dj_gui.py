import wx
import chat_client

FRAME_SIZE = (626, 443)
BACKGROUND = "dj_background.png"

SENDING_SONG_LIST = "SONG_LIST??"

SONG_LIST = ''
SEPARATOR = '##??##'


class WelcomePanel(wx.Panel):
    def __init__(self, parent_frame):
        wx.Panel.__init__(self, parent=parent_frame, size=FRAME_SIZE)

        self.parent_frame = parent_frame  # parent frame.
        self.v_box = wx.BoxSizer(wx.VERTICAL)  # setting a vertical box sizer, to arrange objects on panel.

        self.background = BACKGROUND
        bmp1 = wx.Image(BACKGROUND, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap1 = wx.StaticBitmap(self, -1, bmp1, (0, 0))

        # Displaying a welcome text.
        self.welcome_text = wx.StaticText(self.bitmap1, label="welcome to the DJ stand!",
                                          style=wx.ALIGN_CENTRE | wx.TRANSPARENT_WINDOW)
        self.welcome_text.SetFont(
            wx.Font(30, wx.ROMAN, wx.NORMAL, wx.BOLD, False, u'Arial Rounded MT Bold'))  # setting font.

        self.continue_button = wx.Button(self.bitmap1, label="continue")

        # Binding buttons
        self.continue_button.Bind(wx.EVT_BUTTON, self.button_clicked)

        #  Adding all of the objects in the panel to the sizer.

        self.v_box.AddSpacer(20)
        self.v_box.Add(self.welcome_text, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 40)
        self.v_box.AddSpacer(180)
        self.v_box.Add(self.continue_button, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # Setting our sizer as the panel's sizer.
        self.SetSizer(self.v_box)

    def button_clicked(self, event):
        self.parent_frame.switch_panels()


class SelectSongs(wx.Panel):
    """ in this panel, dj will choose the songs they want to play at the party. """

    def __init__(self, parent_frame):
        wx.Panel.__init__(self, parent=parent_frame, size=FRAME_SIZE)

        self.parent_frame = parent_frame  # parent frame.
        self.v_box = wx.BoxSizer(wx.VERTICAL)  # setting a vertical box sizer, to arrange objects on panel.

        self.background = BACKGROUND
        bmp1 = wx.Image(BACKGROUND, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap1 = wx.StaticBitmap(self, -1, bmp1, (0, 0))

        self.open_file_dialog = wx.FileDialog(self.bitmap1, "Open", "", "", "mp3 files (*.mp3)|*.mp3",
                                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        # Displaying the 'select songs' text.
        self.select_songs_text = wx.StaticText(self.bitmap1, label="Please select the songs to be played",
                                               style=wx.ALIGN_CENTRE | wx.TRANSPARENT_WINDOW)
        self.select_songs_text.SetFont(
            wx.Font(15, wx.ROMAN, wx.NORMAL, wx.BOLD, False, u'Arial Rounded MT Bold'))  # setting font.

        # creating the 'select songs' button
        self.select_song_button = wx.Button(self.bitmap1, label="select a song")
        self.select_song_button.Bind(wx.EVT_BUTTON, self.file_dialog)

        self.continue_button = wx.Button(self.bitmap1, label="continue")
        self.continue_button.Bind(wx.EVT_BUTTON, self.button_clicked)

        #  Adding all of the objects in the panel to the sizer.
        self.v_box.AddSpacer(20)
        self.v_box.Add(self.select_songs_text, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 40)
        self.v_box.AddSpacer(20)
        self.v_box.Add(self.select_song_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 40)
        self.v_box.AddSpacer(20)
        self.v_box.Add(self.continue_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 40)

        # Setting our sizer as the panel's sizer.
        self.SetSizer(self.v_box)

    def file_dialog(self, event):
        self.open_file_dialog.ShowModal()  # opening file dialog
        global SONG_LIST
        SONG_LIST += self.open_file_dialog.GetPath() + SEPARATOR  # Adding song to server's song list.

    def button_clicked(self, event):
        self.parent_frame.switch_panels()


class WaitForClients(wx.Panel):
    """ in this panel, djs will decide when to start the party. """

    def __init__(self, parent_frame):
        wx.Panel.__init__(self, parent=parent_frame, size=FRAME_SIZE)

        self.parent_frame = parent_frame  # parent frame.
        self.v_box = wx.BoxSizer(wx.VERTICAL)  # setting a vertical box sizer, to arrange objects on panel.

        self.background = BACKGROUND
        bmp1 = wx.Image(BACKGROUND, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap1 = wx.StaticBitmap(self, -1, bmp1, (0, 0))

        # Displaying the client counter text text.
        self.client_counter_text = wx.StaticText(self.bitmap1, label="clients waiting for the party:",
                                                 style=wx.ALIGN_CENTRE | wx.TRANSPARENT_WINDOW)
        self.client_counter_text.SetFont(
            wx.Font(15, wx.ROMAN, wx.NORMAL, wx.BOLD, False, u'Arial Rounded MT Bold'))  # setting font.

        self.start_party_button = wx.Button(self.bitmap1, label="start party!")
        self.start_party_button.Bind(wx.EVT_BUTTON, self.button_clicked)

        #  Adding all of the objects in the panel to the sizer.
        self.v_box.AddSpacer(20)
        self.v_box.Add(self.client_counter_text, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 40)
        self.v_box.AddSpacer(20)
        self.v_box.Add(self.start_party_button, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 40)

        # Setting our sizer as the panel's sizer.
        self.SetSizer(self.v_box)

    def button_clicked(self, event):
        self.parent_frame.client.client_socket.send(
            self.parent_frame.client.encrypt_request(SENDING_SONG_LIST + SONG_LIST))
        self.parent_frame.switch_panels()


class Frame(wx.Frame):
    """ main frame. """

    def __init__(self, parent, title):
        super(Frame, self).__init__(parent, title=title, size=FRAME_SIZE,
                                    style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

        self.SetIcon(wx.Icon("icon.ico"))  # setting icon.

        self.welcome_panel = WelcomePanel(self)  # creating and showing the first panel.

        self.client = chat_client.Client(60000)  # creating client.

        self.client.send_key()  # sending key to server.

        # initializing the next panels, afterwards they will become actual objects.
        self.select_songs_panel = wx.Panel(self).Hide()
        self.wait_for_clients_panel = wx.Panel(self).Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)  # setting a vertical box sizer, to arrange objects on panel.
        self.sizer.Add(self.welcome_panel, 1, wx.EXPAND)  # adding panel to sizer.
        self.SetSizer(self.sizer)  # Setting our sizer as the panel's sizer.

    def switch_panels(self):
        """ responsible for switching panels. """
        if self.welcome_panel.IsShownOnScreen():  # if first panel is shown:
            self.welcome_panel.Hide()  # hide panel
            self.sizer.Remove(0)  # remove panel form the sizer
            self.select_songs_panel = SelectSongs(self)  # create the next panel
            self.sizer.Add(self.select_songs_panel, 1, wx.EXPAND)  # add next panel to sizer.
            self.Layout()

        elif self.select_songs_panel.IsShownOnScreen():
            self.select_songs_panel.Hide()  # hide panel
            self.sizer.Remove(0)  # remove panel form the sizer
            self.wait_for_clients_panel = WaitForClients(self)  # create the next panel
            self.sizer.Add(self.wait_for_clients_panel, 1, wx.EXPAND)  # add next panel to sizer.
            self.Layout()


def main():
    app = wx.App()
    frame = Frame(None, title="DJ stand")
    frame.Centre()
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
