import gobject
import pango
import gtk
from gtk import gdk,keysyms
import datetime
from pytz import timezone
from .. extensions.validation import MaskEntry,ValidationError
import time
from .. boss import boss
curr = boss.get_state()

def set_background(widget, color, state=gtk.STATE_NORMAL):
    widget.modify_base(state, gdk.color_parse(color))

class _DateEntryPopup(gtk.Window):
    __gsignals__ = {
            'date-selected': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,(object,)),
            }

    def __init__(self, dateentry):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.add_events(gdk.BUTTON_PRESS_MASK)
        self.connect('key-press-event', self._on__key_press_event)
        self.connect('button-press-event', self._on__button_press_event)
        self._dateentry = dateentry

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.add(frame)
        frame.show()

        vbox = gtk.VBox()
        vbox.set_border_width(6)
        frame.add(vbox)
        vbox.show()
        self._vbox = vbox

        self.calendar = gtk.Calendar()
        self.calendar.connect('day-selected-double-click',
                               self._on_calendar__day_selected_double_click)
        vbox.pack_start(self.calendar, False, False)
        self.calendar.show()

        buttonbox = gtk.HButtonBox()
        buttonbox.set_border_width(6)
        buttonbox.set_layout(gtk.BUTTONBOX_SPREAD)
        vbox.pack_start(buttonbox, False, False)
        buttonbox.show()

        for label, callback in [(_('_Hoy'), self._on_today__clicked),
                                (_('_Cancelar'), self._on_cancel__clicked),
                                (_('_Aceptar'), self._on_select__clicked)]:
            button = gtk.Button(label, use_underline=True)
            button.connect('clicked', callback)
            buttonbox.pack_start(button)
            button.show()

        self.set_resizable(False)
        self.set_screen(dateentry.get_screen())

        self.realize()
        self.height = self._vbox.size_request()[1]

    def _on_calendar__day_selected_double_click(self, calendar):
        self.emit('date-selected', self.get_date())

    def _on__button_press_event(self, window, event):
        # If we're clicking outside of the window close the popup
        hide = False

        # Also if the intersection of self and the event is empty, hide
        # the calendar
        if (tuple(self.allocation.intersect(
              gdk.Rectangle(x=int(event.x), y=int(event.y),
                           width=1, height=1))) == (0, 0, 0, 0)):
            hide = True

        # Toplevel is the window that received the event, and parent is the
        # calendar window. If they are not the same, means the popup should
        # be hidden. This is necessary for when the event happens on another
        # widget
        toplevel = event.window.get_toplevel()
        parent = self.calendar.get_parent_window()
        if toplevel != parent:
            hide = True

        if hide:
            self.popdown()

    def _on__key_press_event(self, window, event):
        keyval = event.keyval
        state = event.state & gtk.accelerator_get_default_mod_mask()
        if (keyval == keysyms.Escape or
            ((keyval == keysyms.Up or keyval == keysyms.KP_Up) and
             state == gdk.MOD1_MASK)):
            self.popdown()
            return True
        elif keyval == keysyms.Tab:
            self.popdown()
            return True
        elif (keyval == keysyms.Return or
              keyval == keysyms.space or
              keyval == keysyms.KP_Enter or
              keyval == keysyms.KP_Space):
            self.emit('date-selected', self.get_date())
            return True

        return False

    def _on_select__clicked(self, button):
        self.emit('date-selected', self.get_date())

    def _on_cancel__clicked(self, button):
        self.popdown()

    def _on_today__clicked(self, button):
        self.set_date(datetime.date.today())

    def _popup_grab_window(self):
        activate_time = 0L
        if gdk.pointer_grab(self.window, True,
                            (gdk.BUTTON_PRESS_MASK |
                             gdk.BUTTON_RELEASE_MASK |
                             gdk.POINTER_MOTION_MASK),
                             None, None, activate_time) == 0:
            if gdk.keyboard_grab(self.window, True, activate_time) == 0:
                return True
            else:
                self.window.get_display().pointer_ungrab(activate_time);
                return False
        return False

    def _get_position(self):
        self.realize()
        calendar = self

        sample = self._dateentry

        # We need to fetch the coordinates of the entry window
        # since comboentry itself does not have a window
        x, y = sample.dateentry.window.get_origin()
        width, height = calendar.size_request()
        height = self.height

        screen = sample.get_screen()
        monitor_num = screen.get_monitor_at_window(sample.window)
        monitor = screen.get_monitor_geometry(monitor_num)

        if x < monitor.x:
            x = monitor.x
        elif x + width > monitor.x + monitor.width:
            x = monitor.x + monitor.width - width

        if y + sample.allocation.height + height <= monitor.y + monitor.height:
            y += sample.allocation.height
        elif y - height >= monitor.y:
            y -= height
        elif (monitor.y + monitor.height - (y + sample.allocation.height) >
              y - monitor.y):
            y += sample.allocation.height
            height = monitor.y + monitor.height - y
        else :
            height = y - monitor.y
            y = monitor.y

        return x, y, width, height

    def popup(self, date):
        """
        Shows the list of options. And optionally selects an item
        @param date: date to select
        """
        combo = self._dateentry
        if not (combo.flags() & gtk.REALIZED):
            return

        treeview = self.calendar
        if treeview.flags() & gtk.MAPPED:
            return
        toplevel = combo.get_toplevel()
        if isinstance(toplevel, gtk.Window) and toplevel.group:
            toplevel.group.add_window(self)

        x, y, width, height = self._get_position()
        self.set_size_request(width, height)
        self.move(x, y)
        self.show_all()

        if date:
            self.set_date(date)
        self.grab_focus()

        if not (self.calendar.flags() & gtk.HAS_FOCUS):
            self.calendar.grab_focus()

        if not self._popup_grab_window():
            self.hide()
            return

        self.grab_add()

    def popdown(self):
        combo = self._dateentry
        if not (combo.flags() & gtk.REALIZED):
            return

        self.grab_remove()
        self.hide_all()

    def get_date(self):
        y, m, d = self.calendar.get_date()
        return datetime.date(y, m + 1, d)

    def set_date(self, date):
        self.calendar.select_month(date.month - 1, date.year)
        self.calendar.select_day(date.day)
        # FIXME: Only mark the day in the curr month?
        self.calendar.clear_marks()
        self.calendar.mark_day(date.day)



class DateEntry(gtk.HBox):
    __gsignals__ = {
            'changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,()),
            }

    def __init__(self,manager,fullpanel=True):
        self.boss = manager
        gtk.HBox.__init__(self)
        self._popping_down = False
        dt = datetime.datetime.now()
        self.date = dt.date()
        self.time = dt.time()
        self.dateformat = "%d/%m/%Y"
        self.timeformat = "%H:%M:%S"

        vbox = gtk.VBox()
        self.dateentry = MaskEntry()
        self.dateentry.set_mask('00/00/0000')
        self.dateentry.connect('changed',self.on_entry_changed)
        self.dateentry.connect('focus_out_event',self.on_entry_focus_out)
        mask = self.dateentry.get_mask()
        self.dateentry.set_width_chars(len(mask))
        hbox1 = gtk.HBox()
        if fullpanel:
            label = gtk.Label("    "+_("Fecha:")+"    ")
            hbox1.pack_start(label,False,False)
            sg = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
            sg.add_widget(label)
        hbox1.pack_start(self.dateentry,False,False)

        self._button = gtk.ToggleButton()
        self._button.connect('scroll-event', self.on_entry_scroll_event)
        self._button.connect('toggled', self.on_button_toggled)
        self._button.set_focus_on_click(False)
        hbox1.pack_start(self._button, False, False)
        self._button.show()

        arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_NONE)
        self._button.add(arrow)
        arrow.show()

        self._popup = _DateEntryPopup(self)
        self._popup.connect('date-selected', self._on_popup__date_selected)
        self._popup.connect('hide', self._on_popup__hide)
        self._popup.set_size_request(-1, 24)

        vbox.pack_start(hbox1,False,False)
        if fullpanel:
            label = gtk.Label(_("Hora:"))
            self.timeentry = MaskEntry()
            self.timeentry.set_mask('00:00:00')
            self.timeentry.connect('changed',self.on_entry_changed)
            self.timeentry.connect('focus_out_event',self.on_entry_focus_out)
            mask = self.timeentry.get_mask()
            self.timeentry.set_width_chars(len(mask))
            hbox2 = gtk.HBox()
            hbox2.pack_start(label,False,False)
            hbox2.pack_start(self.timeentry,False,False)
            sg.add_widget(label)
            vbox.pack_start(hbox2,False,False)
            self.pack_end(self.create_delta_panel(),False,False)

        self.pack_start(vbox,False,False)

    def create_delta_panel(self):
        vbox = gtk.VBox()
        adj = gtk.Adjustment(1,1,15,1,5)
        spin = gtk.SpinButton(adj)
        spin.set_wrap(True)
        spin.set_alignment(1.0)
        self.spin = spin
        vbox.pack_start(spin,False,False)

        hbox = gtk.HBox()
        button = gtk.Button()
        arrow = gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_NONE)
        button.add(arrow)
        button.set_data('dir','<')
        button.set_size_request(26,-1)
        button.connect('clicked',self.on_panel_arrow_clicked)
        hbox.pack_start(button,False,False)

        button = gtk.ToggleButton(_('minutos'))
        button.set_size_request(60,-1)
        button.connect('toggled',self.on_delta_toggled)
        button.connect('scroll-event', self.on_delta_scroll_event)
        self.hintbut = button
        hbox.pack_start(button,False,False)

        button = gtk.Button()
        arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_NONE)
        button.add(arrow)
        button.set_data('dir','>')
        button.set_size_request(26,-1)
        button.connect('clicked',self.on_panel_arrow_clicked)
        hbox.pack_start(button,False,False)
        vbox.pack_start(hbox,False,False)
        return vbox

    def do_grab_focus():
        self.dateentry.grab_focus()

    def on_entry_changed(self,entry):
        self.calc_and_set(entry)

    def on_entry_focus_out(self,entry,event):
        self.calc_and_set(entry)

    def calc_and_set(self,entry):
        if entry is self.dateentry:
            try:
                self.date = self.get_date()
                set_background(entry, "#ffffff")
            except ValidationError, e:
                self.date = None
                set_background(entry, "#ff699a")
        elif entry is self.timeentry:
            try:
                self.time = self.get_time()
                set_background(entry, "#ffffff")
            except ValidationError, e:
                self.time = None
                set_background(entry, "#ff699a")
        if self.date is not None and self.time is not None:
            curr.calcdt.setdt(datetime.datetime.combine(self.date,self.time))
        active = self.boss.mpanel.active_slot
        curr.setchart()
        curr.act_pool(active,curr.calc)

    def set_date(self,date):
        if not isinstance(date,datetime.date):
            raise TypeError("date must be a datetime.date instance")
        if date.year < 1900:
            year = date.year
            month = str(date.month).rjust(2,'0')
            day = str(date.day).rjust(2,'0')
            strdate = "%s/%s/%s" % (day,month,year)
            self.dateentry.set_text(strdate)
        else:
            self.dateentry.set_text(date.strftime(self.dateformat))

    def get_date(self):
        text = self.dateentry.get_text()
        if text == "":
            return None
        try:
            dateinfo = time.strptime(text, self.dateformat)
            return datetime.date(*dateinfo[:3])
        except ValueError:
            raise ValidationError('value error: %s' % text)
        return None

    def set_time(self,time):
        if not isinstance(time,datetime.time):
            raise TypeError("date must be a datetime.time instance")
        self.timeentry.set_text(time.strftime(self.timeformat))

    def get_time(self):
        text = self.timeentry.get_text()
        if text == "":
            return None
        try:
            dateinfo = time.strptime(text, self.timeformat)
            return datetime.time(*dateinfo[3:6])
        except ValueError:
            raise ValidationError('value error: %s' % text)

    def on_entry_scroll_event(self,entry,event):
        if event.direction == gdk.SCROLL_UP:
            amount = 1
        elif event.direction == gdk.SCROLL_DOWN:
            amount = -1
        else:
            return
        try:
            date = self.get_date()
            newdate = date + datetime.timedelta(days=amount)
        except ValidationError:
            newdate = datetime.date.today()
        self.set_date(newdate)

    def on_button_toggled(self,button):
        if self._popping_down:
            return
        try:
            date = self.get_date()
        except ValidationError:
            date = None
        self._popup.popup(date)

    def _on_popup__hide(self, popup):
        self._popping_down = True
        self._button.set_active(False)
        self._popping_down = False

    def _on_popup__date_selected(self, popup, date):
        self.set_date(date)
        popup.popdown()
        self.dateentry.grab_focus()
        self.dateentry.set_position(len(self.dateentry.get_text()))

    def on_panel_arrow_clicked(self,but):
        delta = self.spin.get_value_as_int()
        if but.get_data('dir') == '<':
            delta = -delta
        self.change_on_delta(delta)

    def on_delta_toggled(self,but):
        hint = [_('minutos'),_('horas')]
        lbl = hint[but.get_active()]
        but.set_label(lbl)

    def on_delta_scroll_event(self,entry,event):
        delta = self.spin.get_value_as_int()
        if event.direction == gdk.SCROLL_UP:
            amount = 1 * delta
        elif event.direction == gdk.SCROLL_DOWN:
            amount = -1 * delta
        else:
            return
        self.change_on_delta(amount)

    def change_on_delta(self,delta):
        changes = {_('minutos'):'minutes',_('horas'):'hours'}
        hof = None
        change = changes[self.hintbut.get_label()]
        try:
            time = self.get_time()
        except ValidationError:
            time = None
        if not time:
            time = datetime.time.min
        h = time.hour
        m = time.minute
        s = time.second
        if change == 'minutes':
            mof,m = divmod(m+delta,60)
            if mof:
                hof,h = divmod(h+mof,24)
        else:
            hof,h = divmod(h+delta,24)
        newtime = datetime.time(h,m,s)
        self.set_time(newtime)
        if hof:
            try:
                date = self.get_date()
                newdate = date + datetime.timedelta(days=hof)
            except ValidationError:
                newdate = datetime.date.today()
            self.set_date(newdate)
