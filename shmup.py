# Shmup game
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3 <http://creativecommons.org/licenses/by/3.0/>
# Art from Kenney.nl

import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), "img")
snd_dir = path.join(path.dirname(__file__), "snd")


WIDTH = 480
HEIGHT = 600
FPS = 60

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#initialize pygame and create window
pygame.init()
pygame.mixer.init() #sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
	font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, True, WHITE) #True is for anti-aliasing
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x, y)
	surf.blit(text_surface, text_rect)

def newmob():
	m = Mob()
	all_sprites.add(m)
	mobs.add(m)
	
def draw_shield_bar(surf, x, y, pct):
	if pct < 0:
		pct = 0
	BAR_LENGTH = 100
	BAR_HEIGHT = 10
	fill = (pct / 100) * BAR_LENGTH
	outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
	fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
	pygame.draw.rect(surf, GREEN, fill_rect)
	pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
	for i in range(lives):
		img_rect = img.get_rect()
		img_rect.x = x + 30 * i
		img_rect.y = y
		surf.blit(img, img_rect)
	
class Digit(pygame.sprite.Sprite):
	def __init__(self, digit, seq):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(path.join(img_dir, digit)).convert()
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.topleft = (WIDTH-60-(seq*20), 20)
		
	#def update(self, digit):
	#	self.digit_img = pygame.image.load(path.join(img_dir, "numeral"+digit+".png")).convert()


def update_score(score):
	#print(score)
	score_str = str(score)
	len_score = len(score_str)
	len_scoreboard = len(scoreboard)
	
	for seq in range(len_score):
		digit = scoreboard[len_scoreboard-1-seq]
		digit.image = pygame.image.load(path.join(img_dir, score_str[len_score-1-seq])).convert()
		digit.image.set_colorkey(BLACK)
	
	
class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(player_img, (50, 38))
		self.image.set_colorkey(BLACK)
		#self.image = pygame.Surface((50, 40))
		#self.image.fill(GREEN)
		self.rect = self.image.get_rect()
		self.radius = 20
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.centerx = WIDTH / 2
		self.rect.bottom = HEIGHT - 10
		self.speedx = 0
		self.shield = 100
		self.shoot_delay = 150
		self.last_shot = pygame.time.get_ticks()
		self.lives = 3
		self.hidden = False
		self.hide_timer = pygame.time.get_ticks()
		
	def update(self):
		# unhide if hidden
		if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
			self.hidden = False
			self.rect.centerx = WIDTH / 2
			self.rect.bottom = HEIGHT - 10
			
		self.speedx = 0
		keystate = pygame.key.get_pressed()
		if keystate[pygame.K_a] or keystate[pygame.K_LEFT]:
			self.speedx = -8
		if keystate[pygame.K_d] or keystate[pygame.K_RIGHT]:
			self.speedx = 8
		if keystate[pygame.K_SPACE]:
			self.shoot()
				
		self.rect.x += self.speedx
		
		if self.rect.right > WIDTH:
			self.rect.right = WIDTH
		if self.rect.left < 0:
			self.rect.left = 0
	
	def shoot(self):
		now = pygame.time.get_ticks()
		if now - self.last_shot > self.shoot_delay:
			self.last_shot = now
			bullet = Bullet(self.rect.centerx, self.rect.top)
			all_sprites.add(bullet)
			bullets.add(bullet)
			shoot_sound.play()
	
	def hide(self):
		# hide the player temporarily
		self.hidden = True
		self.hide_timer = pygame.time.get_ticks()
		self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		#self.image = pygame.transform.scale(meteor_img, (43, 43))
		#self.image_orig = meteor_img
		self.image_orig = random.choice(meteor_images)
		self.image_orig.set_colorkey(BLACK)
		self.image = self.image_orig.copy()
		#self.image = pygame.Surface((30, 40))
		#self.image.fill(RED)
		self.rect = self.image.get_rect()
		self.radius = int(self.rect.width * 0.85 / 2)
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.x = random.randrange(WIDTH - self.rect.width)
		self.rect.y = random.randrange(-150, -100)
		self.speedy = random.randrange(1, 8)
		self.speedx = random.randrange(-3,3)
		self.rot = 0
		self.rot_speed = random.randrange(-8, 8)
		self.last_update = pygame.time.get_ticks()
	
	def rotate(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > 50:
			self.last_update = now
			self.rot = (self.rot + self.rot_speed) % 360
			new_image = pygame.transform.rotate(self.image_orig, self.rot)
			old_center = self.rect.center
			self.image = new_image
			self.rect = self.image.get_rect()
			self.rect.center = old_center
			
	
	def update(self):
		self.rotate()
		self.rect.x += self.speedx
		self.rect.y += self.speedy
		if self.rect.top > HEIGHT + 10 or self.rect.right < 0 or self.rect.left > WIDTH:
			self.rect.x = random.randrange(WIDTH - self.rect.width)
			self.rect.y = random.randrange(-100, -40)
			self.speedy = random.randrange(1, 8)
			self.speedx = random.randrange(-3,3)

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(bullet_img, (6, 54))
		self.image.set_colorkey(BLACK)
		#self.image = pygame.Surface((10, 20))
		#self.image.fill(YELLOW)
		self.rect = self.image.get_rect()
		self.rect.bottom = y
		self.rect.centerx = x
		self.speedy = -10
			
	def update(self):
		self.rect.y += self.speedy
		# kill if it moves off the top of the screen
		if self.rect.bottom < 0:
			self.kill()
	
class Pow(pygame.sprite.Sprite):
	def __init__(self, center):
		pygame.sprite.Sprite.__init__(self)
		self.type = random.choice(['shield', 'gun'])
		self.image = powerup_images[self.type]
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.speedy = 5
			
	def update(self):
		self.rect.y += self.speedy
		# kill if it moves off the top of the screen
		if self.rect.top > HEIGHT:
			self.kill()
	
class Explosion(pygame.sprite.Sprite):
	def __init__(self, center, size):
		pygame.sprite.Sprite.__init__(self)
		self.size = size
		self.image = explosion_anim[self.size][0]
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 75
	
	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(explosion_anim[self.size]):
				self.kill()
			else:
				center = self.rect.center
				self.image = explosion_anim[self.size][self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center
	
# load all game graphics
background = pygame.image.load(path.join(img_dir, "starfield.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_orange.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_med1.png', 'meteorBrown_med3.png', 
						'meteorBrown_small1.png', 'meteorBrown_small2.png', 'meteorBrown_tiny1.png', 'meteorBrown_tiny2.png']

for img in meteor_list:
	meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

digits = ["0", "0", "0", "0", "0", "0"]
scoreboard = []

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
	filename = 'regularExplosion0{}.png'.format(i)
	img = pygame.image.load(path.join(img_dir, filename)).convert()
	img.set_colorkey(BLACK)
	img_lg = pygame.transform.scale(img, (75, 75))
	explosion_anim['lg'].append(img_lg)
	img_sm = pygame.transform.scale(img, (32, 32))
	explosion_anim['sm'].append(img_sm)
	filename = 'sonicExplosion0{}.png'.format(i)
	img = pygame.image.load(path.join(img_dir, filename)).convert()
	img.set_colorkey(BLACK)
	explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()
	
# Load all game sounds
#background_sound = pygame.mixer.Sound(path.join(snd_dir, "tgfcoder-FrozenJam-SeamlessLoop.ogg"))
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, "My_Laser2.wav"))
death_sound = pygame.mixer.Sound(path.join(snd_dir, "My_Death1.wav"))
hurt_sound = pygame.mixer.Sound(path.join(snd_dir, "My_Hurt2.wav"))
expl_sounds = [pygame.mixer.Sound(path.join(snd_dir, "My_Explosion1.wav")),
					pygame.mixer.Sound(path.join(snd_dir, "My_Explosion2.wav"))]
pygame.mixer.music.load(path.join(snd_dir, "tgfcoder-FrozenJam-SeamlessLoop.ogg"))
pygame.mixer.music.set_volume(0.4)
	
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
score_digits = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(8):
	newmob()

for i in range(len(digits)):
	digit = Digit(digits[i], len(digits)-1-i)
	scoreboard.append(digit)
	all_sprites.add(digit)
	score_digits.add(digit)
	
score = 0

pygame.mixer.music.play(loops=-1)	
#Game loop
running = True
while running:
	# keep loop running at the right speed
	clock.tick(FPS)
	##### Process Input (events)
	for event in pygame.event.get():
		# check for closing window
		if event.type == pygame.QUIT:
			running = False
	
	##### Update
	all_sprites.update()
	
	# check to see if a bullet hit a mob
	hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
	for hit in hits:
		random.choice(expl_sounds).play()
		score += 50 - hit.radius
		expl = Explosion(hit.rect.center, 'lg')
		all_sprites.add(expl)
		newmob()
		update_score(score)
	
	# check to see if a mob hit the player
	hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle) #True for mob to disappear
	for hit in hits:
		player.shield -= hit.radius*2
		expl = Explosion(hit.rect.center, 'sm')
		all_sprites.add(expl)
		hurt_sound.play()
		newmob()
		if player.shield <= 0:
			death_sound.play()
			death_explosion = Explosion(player.rect.center, 'player')
			all_sprites.add(death_explosion)
			player.hide()
			player.lives -= 1
			player.shield = 100
			#running = False
	
	# if player died and explosion finished playing
	if player.lives == 0 and not death_explosion.alive():
		running = False
		
	##### Draw / render	
	screen.fill(BLACK)
	screen.blit(background, background_rect)
	all_sprites.draw(screen)
	#score_digits.draw(screen)
	draw_text(screen, str(score), 18, WIDTH / 2, 10)
	draw_shield_bar(screen, 5, 5, player.shield)
	draw_lives(screen, 5, 20, player.lives, player_mini_img)
	#update_score(score)
	# *after drawing everything
	pygame.display.flip()

pygame.time.wait(3000)
	
pygame.quit()