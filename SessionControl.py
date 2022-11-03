from . import MIDI
from . import settings
import Live
from .Logging import log

from .Control import Control

class SessionControl(Control):
#	__module__ = __name__
	__doc__ = "Session parameters of SelectedTrackControl"
	
	def __init__(self, c_instance, selected_track_controller):
		Control.__init__(self, c_instance, selected_track_controller)
		
		if settings.auto_select_playing_clip:
			self.song.view.add_selected_track_listener(self.on_track_selected)
	
	def get_midi_bindings(self):
		return (
			("play_selected_scene", self.fire_selected_scene),
			("play_next_scene", self.fire_next_scene),
			("play_prev_scene", self.fire_previous_scene),
			
			("first_scene", self.select_first_scene),
			("last_scene", self.select_last_scene),
			
			("play_selected_clip", self.fire_selected_clip_slot),
			("toggle_selected_clip", self.toggle_selected_clip_slot),
			("play_next_clip", self.fire_next_clip_slot),
			("play_prev_clip", self.fire_previous_clip_slot),
			("play_next_available_clip", self.fire_next_available_clip_slot),
			("play_prev_available_clip", self.fire_previous_available_clip_slot),
			
			("select_playing_clip", self.select_playing_clip),
			("toggle_auto_select_playing_clip", self.toggle_auto_select_playing_clip),
			
			#("toggle_mute_selected_clip", self.toggle_mute_selected_clip),
			
			("stop_all_clips", self.stop_all_clips),
			("stop_selected_track", self.stop_selected_track),
			("disarm_all_tracks", self.disarm_all_tracks),
			
			("first_track", self.select_first_track),
			("last_track", self.select_last_track),
			
			("scroll_scenes", self.scroll_scenes),
			("scroll_tracks", self.scroll_tracks),
			
			("select_scene", self.select_scene),
			("select_track", self.select_track),
			
			("prev_scene", lambda value, mode, status: self.scroll_scene(-1, value, mode, MIDI.CC_STATUS)),
			("next_scene", lambda value, mode, status: self.scroll_scene(1, value, mode, MIDI.CC_STATUS)),
			("prev_track", lambda value, mode, status: self.scroll_track(-1, value, mode, MIDI.CC_STATUS)),
			("next_track", lambda value, mode, status: self.scroll_track(1, value, mode, MIDI.CC_STATUS)),
			("prev_group", lambda value, mode, status: self.scroll_track('prev', value, mode, MIDI.CC_STATUS)),
			("next_group", lambda value, mode, status: self.scroll_track('next', value, mode, MIDI.CC_STATUS)),
			
			("toggle_track_fold", self.toggle_track_fold),


			# Live 9
			("stop_all_clips_immediately", self.stop_all_clips_immediately),

			("create_scene_at", self.create_scene_at), # creates scene at value of MIDI message
			("create_scene_before", lambda value, mode, status: self.create_scene_at(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),
			("create_scene_after", lambda value, mode, status: self.create_scene_at(1, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),
			("create_new_scene", self.create_new_scene),

			("duplicate_scene", self.duplicate_scene), # duplicates scene at value of MIDI message
			("duplicate_selected_scene", lambda value, mode, status: self.duplicate_scene(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),
			
			("capture_scene", self.capture_scene),
			("capture_scene_except_selected", self.capture_scene_except_selected),
			
			("delete_scene", self.delete_scene),# deletes scene at value of MIDI message
			("delete_selected_scene", lambda value, mode, status: self.delete_scene(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),

			("duplicate_track", self.duplicate_track), # duplicates track at value of MIDI message
			("duplicate_selected_track", self.duplicate_track),
			
			("create_midi_track_at", self.create_midi_track_at),
			("create_midi_track_after", lambda value, mode, status: self.create_midi_track_at(1, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),
			("create_midi_track_before", lambda value, mode, status: self.create_midi_track_at(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),

			("create_audio_track_at", self.create_audio_track_at),
			("create_audio_track_after", lambda value, mode, status: self.create_audio_track_at(1, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),
			("create_audio_track_before", lambda value, mode, status: self.create_audio_track_at(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),

			("create_return_track", self.create_return_track),

			("delete_track", self.delete_track),
			("delete_selected_track", self.delete_track),
			
			("delete_device", self.delete_device), # delete device at value of MIDI message on current track
			("delete_selected_device", lambda value, mode, status: self.delete_device(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),

			("duplicate_clip_slot", self.duplicate_clip_slot),
			("duplicate_selected_clip_slot", lambda value, mode, status: self.duplicate_clip_slot(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),

			("delete_clip", self.delete_clip), # delete clip in clipslot at value of MIDI message on current track
			("delete_selected_clip", lambda value, mode, status: self.delete_clip(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)),
		)
	
	
	def auto_arm_track(self, track):
		# fallback to auto-arm if no midi loopback is available
		if settings.auto_arm and not settings.has_midi_loopback:
			if track.can_be_armed:
				track.arm = True
			# for t in self.song.tracks:
			# 	if not t == track and t.can_be_armed:
			# 		t.arm = False
	def disarm_all_tracks(self, value, mode, status):
		if not MIDI.can_trigger(mode, value):
			return
		tracks = self.get_all_tracks()
		for track in tracks:
			if track.can_be_armed:
				track.arm = False
	
	
	def on_track_selected(self):
		self.select_playing_clip(127, MIDI.ABSOLUTE, MIDI.NOTEON_STATUS)
	
	
	def select_playing_clip(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		for clip_slot in self.song.view.selected_track.clip_slots:
			if clip_slot.has_clip and clip_slot.clip.is_playing:
				self.song.view.highlighted_clip_slot = clip_slot
	
	
	def toggle_auto_select_playing_clip(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		settings.auto_select_playing_clip = not settings.auto_select_playing_clip
		if settings.auto_select_playing_clip:
			self.on_track_selected()
			self.song.view.add_selected_track_listener(self.on_track_selected)
		else:
			self.song.view.remove_selected_track_listener(self.on_track_selected)
	
	
	
	def stop_all_clips(self, value, mode, status):
		self.song.stop_all_clips()
	
	
	
	def get_all_tracks(self, only_visible = False):
		tracks = []
		for track in self.song.tracks:
			if not only_visible or track.is_visible:
				tracks.append(track)
				
		for track in self.song.return_tracks:
			tracks.append(track)
		tracks.append(self.song.master_track)
		return tracks

	# helper to determine delta to previous group (or current index if none)
	def get_delta_to_group(self, dir):
		tracks = self.get_all_tracks()
		cur_track_i = 0
		for curi, track in enumerate(tracks):
			if track == self.song.view.selected_track:
				cur_track_i = curi
				cur_group_track = track.group_track
				break
		log(f'current track is {self.song.view.selected_track.name} at {str(cur_track_i)}')
		if cur_group_track:
			log(f'current group is {cur_group_track.name}')
		if dir == 'prev':
			return self.get_delta_to_prev_group(cur_track_i)
		elif dir == 'next':
			for nexi in range(cur_track_i + 1, len(tracks)):
				if cur_group_track and tracks[nexi].group_track == cur_group_track:
					continue
				elif tracks[nexi].group_track == tracks[cur_track_i]:
					continue
				return nexi - cur_track_i + self.get_delta_to_prev_group(nexi + 1) + 1
		log(f' - no prev group, no change')
		return 0
	
	def get_delta_to_prev_group(self, index):
		tracks = self.get_all_tracks()
		group_track = None
		for pexi in reversed(range(0, index)):
			log(str(pexi))
			if not group_track:
				group_track = tracks[pexi].group_track if tracks[pexi].group_track else tracks[pexi]
				log(f'found group-track {group_track.name} at {str(pexi)}')
			if group_track and tracks[pexi] == group_track:
				log(f'matched group {tracks[pexi].name}, delta is {str(pexi - index)}')
				return pexi - index
		return 0

	
	# helper function to go from one track to the other
	def get_track_by_delta(self, track, d_value):
		tracks = self.get_all_tracks(only_visible = True)
		max_tracks = len(tracks)
		for i in range(max_tracks):
			if track == tracks[i]:
				return tracks[max((0, min(i+d_value, max_tracks-1)))]
	
	# helper function to go from one scene to the other
	def get_scene_by_delta(self, scene, d_value):
		scenes = self.song.scenes
		max_scenes = len(scenes)
		for i in range(max_scenes):
			if scene == scenes[i]:
				return scenes[max((0, min(i+d_value, max_scenes-1)))]
	
	
	
	
	
	
	def toggle_track_fold(self, value, mode, status):
		# ignore CC toggles (like on LPD8)
		if status == MIDI.CC_STATUS and not value:
			return
		track = self.song.view.selected_track
		if not track.is_foldable:
			return
		if status == MIDI.NOTEON_STATUS:
			track.fold_state = not track.fold_state
		elif status == MIDI.CC_STATUS:
			if  mode == MIDI.ABSOLUTE:
				track.fold_state = value < 64
			else:
				track.fold_state = value < 0
	
#	def toggle_mute_selected_clip(self, value, mode):
#		log("toggle_mute_selected_clip")
#		clip_slot = self.song.view.highlighted_clip_slot
#		clip = self.song.view.detail_clip
#		#if clip_slot and clip_slot.has_clip():
#		#	clip_slot.clip.muted = not clip_slot.clip.muted
#		
#		if clip:
#			log("clip available")
#			for slot in dir(clip):
#				#try:
#				#	attr = getattr(clip, slot)
#				#except:
#				#	attr = 'no_attr'
#				#log(attr+", "+slot)
#				log(slot)
#			log(getattr(clip, '__doc__', None) or 'no documentation')
#		else:
#			log("no clip available")
#		
#		log("toggle_mute_selected_clip done")
	
	def fire_selected_scene(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		self.song.view.selected_scene.fire()
	
	def fire_next_scene(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		scene = self.get_scene_by_delta(self.song.view.selected_scene, 1)
		scene.fire()
		self.song.view.selected_scene = scene
		
	def fire_previous_scene(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		scene = self.get_scene_by_delta(self.song.view.selected_scene, -1)
		scene.fire()
		self.song.view.selected_scene = scene
	
	# value is overriden by lambda to control direction
	# also, trigger mode will only respond to value of 127 (button down on fcb-505)
	def scroll_scene(self, dir, value, mode, status):
		if not MIDI.can_trigger(mode, value):
			return
		self.scroll_scenes(MIDI.RELATIVE_TWO_COMPLIMENT, value, status, dir)

	def scroll_scenes(self, mode, value, status, dir = None):
		log(f' >>> scroll scene dir {dir}, mode {mode}, value {value}')
		if mode == MIDI.ABSOLUTE:
			# invert value (127-value), somehow feels more natural to turn left to go fully down and right to go up
			# also when assigning this to a fader this is more natural as up is up and down is down
			index = int((127-value)/(128.0/len(self.song.scenes)))
			self.song.view.selected_scene = self.song.scenes[index]
		else:
			self.song.view.selected_scene = self.get_scene_by_delta(self.song.view.selected_scene, dir)
	def select_first_scene(self, value, mode, status):
		if (status == MIDI.CC_STATUS and not value) or not MIDI.can_trigger(mode, value):
			return
		self.song.view.selected_scene = self.song.scenes[0]
	def select_last_scene(self, value, mode, status):
		if (status == MIDI.CC_STATUS and not value) or not MIDI.can_trigger(mode, value):
			return
		self.song.view.selected_scene = self.song.scenes[len(self.song.scenes)-1]
	
	
	# value is overriden by lambda to control direction
	# also, trigger mode will only respond to value of 127 (button down on fcb-505)
	def scroll_track(self, dir, value, mode, status):
		if not MIDI.can_trigger(mode, value):
			return
		if dir == 'prev':
			dir = self.get_delta_to_group('prev')
		elif dir == 'next':
			dir = self.get_delta_to_group('next')
		self.scroll_tracks(MIDI.RELATIVE_TWO_COMPLIMENT, value, status, dir)
	def scroll_tracks(self, value, mode, status, dir = None):
		if mode == MIDI.ABSOLUTE:
			tracks = self.get_all_tracks(only_visible = True)
			index = int(value/(128.0/len(tracks)))
			self.song.view.selected_track = tracks[index]
		else:
			log(f'>>scroll track {str(dir)}')
			next_track = self.get_track_by_delta(self.song.view.selected_track, dir)
			log(f' >>next track {next_track.name}')
			self.song.view.selected_track = next_track
		self.auto_arm_track(self.song.view.selected_track)
	
	
	
	def select_first_track(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		tracks = self.song.tracks
		if self.song.view.selected_track == self.song.master_track:
			self.song.view.selected_track = tracks[len(tracks)-1]
		else:
			self.song.view.selected_track = tracks[0]
		
		self.auto_arm_track(self.song.view.selected_track)
	
	def select_last_track(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		if self.song.view.selected_track == self.song.master_track:
			return
		
		tracks = self.song.tracks
		# mimics Live's behaviour: if last track is selected, select master-track
		if self.song.view.selected_track == tracks[len(tracks)-1]:
			self.song.view.selected_track = self.song.master_track
		else:
			self.song.view.selected_track = tracks[len(tracks)-1]
		
		self.auto_arm_track(self.song.view.selected_track)
	
	def stop_selected_track(self, value, mode, status):
		if not MIDI.can_trigger(mode, value):
			return
		if status == MIDI.CC_STATUS and not value:
			return
		self.song.view.selected_track.stop_all_clips()
		self.song.view.selected_track.arm = False
	
	
	
	
	def select_scene(self, value, mode, status):
		scenes = self.song.scenes
		index = min(len(scenes)-1, value)
		self.song.view.selected_scene = scenes[index]
	
	def select_track(self, value, mode, status):
		tracks = self.song.tracks
		index = min(len(tracks)-1, value)
		self.song.view.selected_track = tracks[index]
	
	
	def fire_selected_clip_slot(self, value, mode, status):
		# to support launch mode "Gate" with CC launchers, one has to react to CC with value 0 as well
		# comment next two lines to support "Gate" launch mode on clips with CC
		#if status == MIDI.CC_STATUS and not value:
		#	return
		if not MIDI.can_trigger(mode, value):
			return
		if self.song.view.highlighted_clip_slot:
			if status == MIDI.NOTEON_STATUS:
				value = 1
			elif value <= 0 or status == MIDI.NOTEOFF_STATUS:
				value = 0
			else:
				value = 1
			self.auto_arm_track(self.song.view.selected_track)
			self.song.view.highlighted_clip_slot.set_fire_button_state(value) #fire()
	
	def toggle_selected_clip_slot(self, value, mode, status):
		clip_slot = self.song.view.highlighted_clip_slot
		if clip_slot and clip_slot.has_clip and not (clip_slot.clip.is_playing or clip_slot.clip.is_triggered):
			self.fire_selected_clip_slot(value, mode, status)
		else:
			self.stop_selected_track(value, mode, status)
	
	def get_clip_slot_by_delta_bool(self, current_clip_slot, track, d_value, bool_callable):
		clip_slots = track.clip_slots
		max_clip_slots = len(clip_slots)
		
		found = False
		if d_value > 0:
			the_range = list(range(max_clip_slots))
		else:
			the_range = list(range(max_clip_slots-1, -1, -1))
		
		for i in the_range:
			clip_slot = clip_slots[i]
			if found and bool_callable(clip_slot):
				return clip_slot
			
			if clip_slot == current_clip_slot:
				found = True
		
		
	
	def fire_clip_slot_by_delta(self, d_value, available):
		current_clip_slot = self.song.view.highlighted_clip_slot
		track = self.song.view.selected_track
		
		if available:
			if track.arm:
				clip_slot = self.get_clip_slot_by_delta_bool(current_clip_slot, track, d_value, lambda x: x.has_stop_button and not x.has_clip)
			else:
				clip_slot = self.get_clip_slot_by_delta_bool(current_clip_slot, track, d_value, lambda x: x.has_clip)
		else:
			clip_slot = self.get_clip_slot_by_delta_bool(current_clip_slot, track, d_value, lambda x: True)
		
		if clip_slot:
			clip_slot.fire()
			self.song.view.highlighted_clip_slot = clip_slot
	
	
	def fire_next_clip_slot(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		self.fire_clip_slot_by_delta(1, False)
		
	def fire_next_available_clip_slot(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		self.fire_clip_slot_by_delta(1, True)
	
	def fire_previous_clip_slot(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		self.fire_clip_slot_by_delta(-1, False)
		
	def fire_previous_available_clip_slot(self, value, mode, status):
		if status == MIDI.CC_STATUS and not value:
			return
		self.fire_clip_slot_by_delta(-1, True)




	# Live 9

	# helper function
	def _get_index_of_element(self, element, elements, d_value = 0):
		max_elements = len(elements)
		for i in range(max_elements):
			if element == elements[i]:
				return max((0, min(i+d_value, max_elements)))
		# if element not found, return end position?
		return max_elements
		# cannot use .index because Live 9 changed it to type "Vector"
		#return max((0, min(elements.index(element)+d_value, max_elements)))
		

	def get_scene_index(self, value, mode, status):
		if mode == MIDI.ABSOLUTE:
			# get scene at index given in value 
			# if value to big then get last possible
			# usually values in absolute mode are greater 0, but make sure they are
			return max(0, min(value, len(self.song.scenes)))
		else:
			# relative to selected scene
			return self._get_index_of_element(self.song.view.selected_scene, self.song.scenes, value)

	def get_track_index(self, value, mode, status):
		if mode == MIDI.ABSOLUTE:
			# get track at index given in value 
			# if value to big then get last possible
			# usually values in absolute mode are greater 0, but make sure they are
			return min(value, len(self.song.tracks))
		else:
			# relative to selected track
			return self._get_index_of_element(self.song.view.selected_track, self.song.tracks, value)

	def get_clipslot_index(self, value, mode, status):
		if mode == MIDI.ABSOLUTE:
			# get clip_slot at index given in value 
			# if value to big then get last possible
			# usually values in absolute mode are greater 0, but make sure they are
			return min(value, len(self.song.view.selected_track.clip_slots))
		else:
			# relative to selected clip_slot
			return self._get_index_of_element(self.song.view.highlighted_clip_slot, self.song.view.selected_track.clip_slots, value)
		
#	def get_device_index(self, value, mode, status):
#		track = self.song.view.selected_track
#		if mode == MIDI.ABSOLUTE:
#			return min(value, len(track.devices))
#		else:
#			return self._get_index_of_element(track.view.selected_device, track.devices, value)



	def stop_all_clips_immediately(self, value, mode, status):
		self.song.stop_all_clips(False)

	def create_scene_at(self, value, mode, status):
		self.song.create_scene(self.get_scene_index(value, mode, status))

	def create_new_scene(self, value, mode, status):
		if not MIDI.can_trigger(mode, value):
			return
		self.song.create_scene(-1)

	def duplicate_scene(self, value, mode, status):
		self.song.duplicate_scene(self.get_scene_index(value, mode, status))
		
	def capture_scene(self, value, mode, status):
		self.song.capture_and_insert_scene(Live.Song.CaptureMode.all)

	def capture_scene_except_selected(self, value, mode, status):
		self.song.capture_and_insert_scene(Live.Song.CaptureMode.all_except_selected)

	def delete_scene(self, value, mode, status):
		self.song.delete_scene(self.get_scene_index(value, mode, status))




	def duplicate_track(self, value, mode, status):
		if not MIDI.can_trigger(mode, value):
			return
		src_track_index = self.get_track_index(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)
		src_is_solo = self.song.view.selected_track.solo
		self.song.duplicate_track(src_track_index)
		# delete all clips in new track - I just want the config
		for clip_slot in self.song.view.selected_track.clip_slots:
			if clip_slot.has_clip:
				clip_slot.delete_clip()
		# if the src-track is solo'd apply same solo
		if src_is_solo:
			self.song.view.selected_track.solo = True


	def create_midi_track_at(self, value, mode, status):
		self.song.create_midi_track(self.get_track_index(value, mode, status))

	def create_audio_track_at(self, value, mode, status):
		self.song.create_audio_track(self.get_track_index(value, mode, status))

	def create_return_track(self, value, mode, status):
		self.song.create_return_track()

	def delete_track(self, value, mode, status):
		if not MIDI.can_trigger(mode, value):
			return
		# works with grouped tracks too
		self.song.delete_track(self.get_track_index(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS))



	def _get_device_index_recursive(self, device, container):
		max_elements = len(container.devices)
		for i in range(max_elements):
			d = container.devices[i]
			if device == d:
				return (container, i, None)
			elif d.can_have_chains:
				for chain in d.chains:
					result = self._get_device_index_recursive(device, chain)
					if result:
						return (result[0], result[1], d)
		return None

	def delete_device(self, value, mode, status):
		container = self.song.view.selected_track
		if mode == MIDI.ABSOLUTE:
			index = min(value, len(container.devices))
		else:
			# find selected device in tracks and device racks (chains)
			result = self._get_device_index_recursive(container.view.selected_device, container)
			if not result:
				return
			container, index, parent_device = result # container is either track or chain

		
		container.delete_device(index)
		# select previous or parent device (mimics default behaviour in GUI)
		if index > 0:
			index-= 1
		if len(container.devices) > index:
			self.song.view.select_device(container.devices[index])
		elif parent_device:
			# container is a chain, therefore ther is a parent_device (device rack)
			self.song.view.select_device(parent_device)

		#self.song.view.selected_track.delete_device(self.get_device_index(value, mode, status))
		
		

	def duplicate_clip_slot(self, value, mode, status):
		index = self.get_clipslot_index(value, mode, status)
		clip_slot = self.song.view.selected_track.clip_slots[index]
		if clip_slot.has_clip:
			# duplicate and select duplicated clipslot
			self.song.view.selected_track.duplicate_clip_slot(index)
			self.song.view.highlighted_clip_slot = self.song.view.selected_track.clip_slots[index+1]
		

	def delete_clip(self, value, mode, status):
		if not MIDI.can_trigger(mode, value):
			return
		clip_slot = self.song.view.selected_track.clip_slots[self.get_clipslot_index(0, MIDI.RELATIVE_TWO_COMPLIMENT, MIDI.CC_STATUS)]
		if clip_slot.has_clip:
			clip_slot.delete_clip()
		

