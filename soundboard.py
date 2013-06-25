import pygame
import pygame.midi
from pygame.locals import *
from time import sleep

class soundsfx:
    def __init__(self, mysound, midikey, ltype, name, options):
        self.mysound = mysound
        self.midikey = midikey
        self.ltype = ltype
        self.name = name
        self.options = options
        
class soundsdb:
    def __init__(self):
        self.data = []
    def add(self, soundobj):
        self.data.append(soundobj)
    def delete(self, soundobj):
        self.data.remove(soundobj)
    
    def writeout(self):
        pass
    def load(self, filename):
        self.data = soundsdbparse(filename)
        
def soundsdbparse(filename):
    return []


#### HERE STARTS THE MEAT
####

pygame.init()

event_get = pygame.event.get
event_post = pygame.event.post

pygame.midi.init()

for i in range(pygame.midi.get_count()):
    r = pygame.midi.get_device_info(i)
    (interf, name, input, output, opened) = r
    in_out = ""
    if input:
        in_out = "(input)"
    if output:
        in_out = "(output)"

    print ("%2i: interface :%s:, name :%s:, opened :%s:  %s" % (i, interf, name, opened, in_out))

#input_device = raw_input('See list above. Please enter the number for your midi input device: ')
input_device = 2 ### TEMPORARY
midi_in = pygame.midi.Input( int(input_device) ) 

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.mixer.set_num_channels(32)

pygame.display.set_caption("MIDI Test")
screen = pygame.display.set_mode((640, 480), RESIZABLE, 32)

sound1 = soundsfx(pygame.mixer.Sound("sword1.wav"), "48", 'oneshot', 'Sword', False)

scene = soundsdb()
scene.add(sound1)

ev_end_oneshot = pygame.USEREVENT+1
ev_end_looping = pygame.USEREVENT+2
ev_end_interval = pygame.USEREVENT+3
ev_pressnote = pygame.USEREVENT+4

assignednotes = {}
assignednotes[48] = {'sound':pygame.mixer.Sound("sword1.wav"),
                     'type':'oneshot',
                     'name':'sword clang',
                     'options':[],
                     'status':0,
                     'channel':None }

channels = range(pygame.mixer.get_num_channels())
channels.reverse()
print channels

print "Starting..."
active = True

while active:
    events = event_get()
    for e in events:
        
        if e.type in [QUIT]:
            active = False
            
        if e.type == ev_end_oneshot:
            '''
            e.code will return the channel which threw the event, i.e. where the sound finished playing.
            Find out which sound was assigned to that channel, and reset its status. (How?)
            '''
            for note in iter(assignednotes):
                if assignednotes[note]['channel'] == e.code:
                    assignednotes[note]['status'] -= 1
                    assignednotes[note]['channel'] = None
                    channels.append(e.code)
                    
        if e.type == ev_end_looping:
            '''
            Queue sound again in same channel
            '''
            pass
        
        if e.type == ev_end_interval:
            '''
            Set random delay based on sound parameters, then play again later (timing mechanic how?)
            '''
            pass
        
        if e.type == ev_pressnote:
            '''
            The logic of this part:
            1. Check if note is already assigned to a sound
            2. If no, assign it --> seperate thing, tbd
            3. If yes, Check if this note is already playing
                4. If yes, proceed to flowchart
                    a. oneshot: do nothing
                    b. looping: stop with fadeout
                    c. interval: cancel interval
                5. If no, play it now! (and do whatever else needs doing)
            '''
            if e.note in assignednotes:
                
                note = assignednotes[e.note]
                
                if note['status'] <= 4: # 'status' in case of oneshots meaning: how often it's currently playing.
                    
                    if note['type'] == 'oneshot':
                        note['channel'] = channels.pop()
                        
                        print 'Playing sound "' + note['name'] + '" on channel ' + str(note['channel'])
                        
                        pygame.mixer.Channel(note['channel']).queue(note['sound'])
                        note['status'] += 1
                        pygame.mixer.Channel(note['channel']).set_endevent(ev_end_oneshot)
                    
                    if note['type'] == 'looping':
                        print "Looped sounds not implemented yet"
                    
                    if note['type'] == 'interval':
                        print "Interval sounds not implemented yet"
                
                elif note['status'] == 1:
                    '''
                    Do what should be done when a oneshot note is played again while still playing
                    '''
                    pass
            
            else:
                '''
                Open dialog to assign new note to this key
                '''
                print "Unassigned key. Key setup tbd."
                pass 
    
    # Check for new MIDI events:
            
    if midi_in.poll():
        midi_events = midi_in.read( 10 )
        for m_e in midi_events:
            if m_e[0][0] == 144:
                event_post(pygame.event.Event(ev_pressnote, note=m_e[0][1]))
    
    pygame.display.update()
    sleep(0.005) # Time in seconds.

print "Exiting..."
del midi_in
pygame.quit()
exit()