import pygame
import pygame.midi
from pygame.locals import *
from time import sleep

def find_channel():
    for c in channelmap:
        if channelmap[c] == None:
            chan = c
            break
    return chan

def start_sound(chan, note, endevent, loops=0, fade=0):
    pygame.mixer.Channel(chan).play(assignednotes[note]['sound'], loops=loops, fade_ms=fade)
    channelmap[chan] = note
    pygame.mixer.Channel(chan).set_endevent(endevent)

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

# Set custom event codes:
ev_end_oneshot = pygame.USEREVENT+1
ev_end_looping = pygame.USEREVENT+2
ev_cont_looping = pygame.USEREVENT+3
ev_end_interval = pygame.USEREVENT+4
ev_cont_interval = pygame.USEREVENT+5
ev_pressnote = pygame.USEREVENT+6

# Prepare data for testing purposes. Later here: Load data from config files.
assignednotes = {}
assignednotes[48] = {'sound':pygame.mixer.Sound("sword1.wav"), # 48 is the midi note for the standard C key
                     'type':'oneshot', # oneshot, looping, or interval
                     'name':'Sword Clang',
                     'options':[4], # tbd - current use: maxchannels for oneshot
                     } 
assignednotes[50] = {'sound':pygame.mixer.Sound("rocket.wav"), 
                     'type':'oneshot', 
                     'name':'Rocket Explosion',
                     'options':[2], 
                     } 
assignednotes[52] = {'sound':pygame.mixer.Sound("sonarping.wav"),
                     'type':'looping',
                     'name':'Sonar Ping',
                     'options':[], # tbd for looping
                     }
assignednotes[53] = {'sound':pygame.mixer.Sound("attack.wav"),
                     'type':'interval',
                     'name':'Sword Hit',
                     'options':[], # tbd for interval
                     }
assignednotes[55] = {'sound':pygame.mixer.Sound("rumbling.aiff"),
                     'type':'looping',
                     'name':'Underwater rumbling',
                     'options':[], # tbd for looping
                     }

channelmap = {} # format: [Channel (int)]:[Note (int)]
for i in range(pygame.mixer.get_num_channels()):
    channelmap[i] = None

print "Starting..."
active = True

while active:
    
    for e in event_get():
        print 'GOT', e
        
        if e.type in [QUIT]:
            active = False
            
        if e.type == ev_end_oneshot:
            '''
            e.code will return the channel which threw the event, i.e. where the sound finished playing.
            Find out which sound was assigned to that channel, and reset its status. (How?)
            '''
            print 'Releasing channel', e.code
            channelmap[e.code] = None
                    
        if e.type == ev_cont_looping:
            '''
            Do nothing, because sound will continue looping on same channel until stopped
            '''
        
        if e.type == ev_end_looping:
            '''
            Stop looping
            '''
            channelmap[e.code] = None
        
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
                print 'Currently assigned channels:', channelmap
                if note['type'] == 'oneshot':
                    # check how often the sound is playing
                    note_concurrent_instances = 0
                    for n in channelmap:
                        if channelmap[n] != None and channelmap[n] == e.note:
                            note_concurrent_instances += 1
                    
                    if note_concurrent_instances < note['options'][0]:
                        # find free channel:
                        chan = find_channel()
                        
                        # now play sound on that channel
                        print 'Playing oneshot sound "' + note['name'] + '" on channel ' + str(chan)
                        start_sound(chan, e.note, ev_end_oneshot)
                    
                if note['type'] == 'looping':
                    # check if sound is already playing
                    playing = False
                    for n in channelmap:
                        if channelmap[n] != None and channelmap[n] == e.note:
                            playing = True
                    
                    if not playing:
                        chan = find_channel()
                        print 'Playing looping sound "' + note['name'] + '" on channel ' + str(chan)
                        start_sound(chan, e.note, ev_cont_looping, -1, 1000) # replace with fade-time from config
                        
                    else:
                        # stop playing
                        print 'Stopping loop of "' + note['name'] +'"'
                        print 'Looking for channel...'
                        for c in channelmap:
                            if channelmap[c] == e.note:
                                print 'Channel found:', c
                                chan = c
                                break
                        pygame.mixer.Channel(chan).set_endevent(ev_end_looping)
                        pygame.mixer.Channel(chan).fadeout(1000) # replace with time loaded from config
                
                if note['type'] == 'interval':
                    print "Interval sounds not implemented yet"
                
            else:
                '''
                Open dialog to assign new note to this key
                '''
                print "Unassigned key. Key setup tbd."
    
    # Check for new MIDI events:
            
    if midi_in.poll():
        midi_events = midi_in.read( 10 )
        for m_e in midi_events:
            if m_e[0][0] == 144: # 144 is the MIDI code for a note press (128 would be note release, which might be useful) 
                event_post(pygame.event.Event(ev_pressnote, note=m_e[0][1]))
    
    pygame.display.update()
    sleep(0.01) # Time in seconds.

print "Exiting..."
del midi_in
pygame.quit()
exit()