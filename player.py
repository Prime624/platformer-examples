"""
This module is used to hold the Player class. The Player represents the user-
controlled sprite on the screen.
"""
import pygame
 
import constants
 
from platforms import MovingPlatform
from spritesheet_functions import SpriteSheet
 
class Player(pygame.sprite.Sprite):
	""" This class represents the bar at the bottom that the player
	controls. """
 
	# -- Attributes
	# Set speed vector of player
	change_x = 0
	change_y = 0
 
	# This holds all the images for the animated walk left/right
	# of our player
	walking_frames_l = []
	walking_frames_r = []
 
	# What direction is the player facing?
	direction = "R"
	
	### This variable represents the stage in the squish animation that the player is currently in.
	### -1 is not ready to bounce, 0 is ready but not started, and 1+ is mid-bounce.
	bouncing=0
	### True if bouncing from the bottom, false if bouncing on the head.
	bounce_bottom=True
	### This is used so that when the player bumps a ceiling, he won't fall down until he is done bouncing.
	### Gravity doesn't look paused in the game.
	pause_grav=False
	### Factor to squish by at each stage. Formula is at bottom of file. Change to stretch also down there.
	### The first two numbers should be 0. They are for when the character isn't bouncing.
	### You CAN CHANGE the other numbers to your liking.
	squish_factor=[0,0,13,9,6,4,6,9,13]
	### Keeps track of the height of the character at different stages in the bounce. Saves unneccessary calculations.
	height_squish=[]
	### The bounce will last for the amount of squishes (in frames)(-2 for when not squished).
	bounce_duration=len(squish_factor)-2
	### The following three variables slow down the framerate slightly when bouncing.
	### The effect does not look slowed down, but it exaggerates the bounce in a good way.
	### These specific numbers look the best to me, but CAN BE CHANGED to exaggerate the effect.
	### The framerate at regular speed.
	tick_tock_fast=60
	### The framerate when bouncing.
	tick_tock_slow=50
	### The framerate will begin at normal speed.
	tick_tock=tick_tock_fast
 
	# List of sprites we can bump against
	level = None
 
	# -- Methods
	def __init__(self):
		""" Constructor function """
 
		# Call the parent's constructor
		pygame.sprite.Sprite.__init__(self)
 
		sprite_sheet = SpriteSheet("p1_walk.png")
		# Load all the right facing images into a list
		image = sprite_sheet.get_image(0, 0, 66, 90)
		self.walking_frames_r.append(image)
		image = sprite_sheet.get_image(66, 0, 66, 90)
		self.walking_frames_r.append(image)
		image = sprite_sheet.get_image(132, 0, 67, 90)
		self.walking_frames_r.append(image)
		image = sprite_sheet.get_image(0, 93, 66, 90)
		self.walking_frames_r.append(image)
		image = sprite_sheet.get_image(66, 93, 66, 90)
		self.walking_frames_r.append(image)
		image = sprite_sheet.get_image(132, 93, 72, 90)
		self.walking_frames_r.append(image)
		image = sprite_sheet.get_image(0, 186, 70, 90)
		self.walking_frames_r.append(image)
 
		# Load all the right facing images, then flip them
		# to face left.
		image = sprite_sheet.get_image(0, 0, 66, 90)
		image = pygame.transform.flip(image, True, False)
		self.walking_frames_l.append(image)
		image = sprite_sheet.get_image(66, 0, 66, 90)
		image = pygame.transform.flip(image, True, False)
		self.walking_frames_l.append(image)
		image = sprite_sheet.get_image(132, 0, 67, 90)
		image = pygame.transform.flip(image, True, False)
		self.walking_frames_l.append(image)
		image = sprite_sheet.get_image(0, 93, 66, 90)
		image = pygame.transform.flip(image, True, False)
		self.walking_frames_l.append(image)
		image = sprite_sheet.get_image(66, 93, 66, 90)
		image = pygame.transform.flip(image, True, False)
		self.walking_frames_l.append(image)
		image = sprite_sheet.get_image(132, 93, 72, 90)
		image = pygame.transform.flip(image, True, False)
		self.walking_frames_l.append(image)
		image = sprite_sheet.get_image(0, 186, 70, 90)
		image = pygame.transform.flip(image, True, False)
		self.walking_frames_l.append(image)
 
		# Set the image the player starts with
		self.image = self.walking_frames_r[0]
 
		# Set a reference to the image rect.
		self.rect = self.image.get_rect()
		### Keeps track of heights of character.
		self.height_orig=self.rect.height
		for i in range(len(self.squish_factor)):
			self.height_squish.append(squish(self.image,self.squish_factor[i]).get_rect().height)
 
	def update(self):
		""" Move the player. """
		### If player isn't bouncing...
		if self.bouncing<1:
			### ...and he's moving down...
			if self.change_y>0:
				### ...set bounce state to ready...
				self.bouncing=0
				### ...and he will be bouncing on his bottom.
				self.bounce_bottom=True
			### (do opposite if going up)
			elif self.change_y<0:
				self.bouncing=0
				self.bounce_bottom=False
		
		# Gravity
		self.calc_grav()
		
		### If has been bouncing longer than should be...
		if self.bouncing>self.bounce_duration:
			### ...stop bounce...
			self.bouncing=-1
			### ...upause gravity (if it was paused)...
			self.pause_grav=False
			### ...and set framerate back to normal.
			self.tick_tock=self.tick_tock_fast
		 
		# Move left/right
		self.rect.x += self.change_x
		pos = self.rect.x + self.level.world_shift
		if self.direction == "R":
			frame = (pos // 30) % len(self.walking_frames_r)
			### Draws character with correct squish factor and direction.
			self.image = squish(self.walking_frames_r[frame],self.squish_factor[self.bouncing+1])
		else:
			frame = (pos // 30) % len(self.walking_frames_l)
			### Draws character with correct squish factor and direction.
			self.image = squish(self.walking_frames_l[frame],self.squish_factor[self.bouncing+1])
		
		### If its height isn't the correct height...
		if self.rect.height!=self.height_squish[self.bouncing+1]:
			### ...then change the height and the position to be correct.
			if self.bounce_bottom:
				self.rect.y+=self.rect.height-self.height_squish[self.bouncing+1]
				self.rect.height=self.height_squish[self.bouncing+1]
			else:
				self.rect.height=self.height_squish[self.bouncing+1]
 
		# See if we hit anything
		block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
		for block in block_hit_list:
			# If we are moving right,
			# set our right side to the left side of the item we hit
			if self.change_x > 0:
				self.rect.right = block.rect.left
			elif self.change_x < 0:
				# Otherwise if we are moving left, do the opposite.
				self.rect.left = block.rect.right
 
		# Move up/down
		self.rect.y += self.change_y
 
		# Check and see if we hit anything
		block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
		for block in block_hit_list:
 
			# Reset our position based on the top/bottom of the object.
			if self.change_y > 0:
				self.rect.bottom = block.rect.top
				### If player has recently landed on a platform...
				if self.bouncing>-1:
					### ...progress bounce state...
					self.bouncing+=1
					### ...set is bouncing on bottom (just in case it isn't already)...
					self.bounce_bottom=True
					### ...and set the framerate to the slower number.
					self.tick_tock=self.tick_tock_slow
			elif self.change_y < 0:
				self.rect.top = block.rect.bottom
				### Do the same if bouncing on head...
				if self.bouncing>-1:
					self.bouncing+=1
					self.bounce_bottom=False
					### ...additionally pausing gravity.
					self.pause_grav=True
					self.tick_tock=self.tick_tock_slow
 
			# Stop our vertical movement
			self.change_y = 0
 
			if isinstance(block, MovingPlatform):
				self.rect.x += block.change_x
 
	def calc_grav(self):
		""" Calculate effect of gravity. """
		if not self.pause_grav:
			if self.change_y == 0:
				self.change_y = 1
			else:
				self.change_y += .35
		else:
			self.bouncing+=1
 
		# See if we are on the ground.
		if self.rect.y >= constants.SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
			self.change_y = 0
			self.rect.y = constants.SCREEN_HEIGHT - self.rect.height
			### Same thing as if player has landed on platform (see line 185).
			if self.bouncing>-1:
				self.bouncing+=1
				self.bounce_bottom=True
				self.tick_tock=self.tick_tock_slow
 
	def jump(self):
		""" Called when user hits 'jump' button. """
 
		# move down a bit and see if there is a platform below us.
		# Move down 2 pixels because it doesn't work well if we only move down 1
		# when working with a platform moving down.
		self.rect.y += 2
		platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
		self.rect.y -= 2
 
		# If it is ok to jump, set our speed upwards
		if len(platform_hit_list) > 0 or self.rect.bottom >= constants.SCREEN_HEIGHT:
			self.change_y = -10
			### Resets squish if player jumps.
			self.tick_tock=self.tick_tock_fast
			self.bouncing=0
			if self.rect.height!=self.height_squish[self.bouncing+1]:
				self.rect.y+=self.rect.height-self.height_squish[self.bouncing+1]
				self.rect.height=self.height_squish[self.bouncing+1]
 
	# Player-controlled movement:
	def go_left(self):
		""" Called when the user hits the left arrow. """
		self.change_x = -6
		self.direction = "L"
 
	def go_right(self):
		""" Called when the user hits the right arrow. """
		self.change_x = 6
		self.direction = "R"
 
	def stop(self):
		""" Called when the user lets off the keyboard. """
		self.change_x = 0

### Method to "squish" images by a certain factor.
def squish(image,factor):
	### If true, player will be stretched instead of squished. Doesn't look very good.
	stretch_instead_of_squish=False
	### Can't divide by 0, so just return original image. Else, see formula.
	if factor==0:
		return image
	elif not stretch_instead_of_squish:
		return pygame.transform.scale(image,(image.get_size()[0],image.get_size()[1]-int(image.get_size()[1]/factor)))
	else:
		return pygame.transform.scale(image,(image.get_size()[0],image.get_size()[1]+int(image.get_size()[1]/factor)))
