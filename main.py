import pygame
from pygame.locals import * 
import sys
import numpy as np
import random
import time
import asyncio

# 定数の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CHARCOAL = (64, 64, 64)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
YELLOW = (255, 155, 0)
BOM_NUM = 12
HORIZONTAL = 10
VERTICAL = 10
GRID_SIZE = 50
WIDTH = GRID_SIZE*HORIZONTAL
HEIGHT = GRID_SIZE*VERTICAL

#pygame初期化
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("マインスイーパ　爆弾数：" + str(BOM_NUM))

class MineSweeper:

    ###初期化
    def __init__(self):
        self.board = np.zeros((VERTICAL, HORIZONTAL), dtype=int)
        self.is_opened = np.zeros((VERTICAL, HORIZONTAL), dtype=bool)
        self.set_bomb()
        
        for i in range(VERTICAL):   #周りの爆弾個数を計算
            for j in range(HORIZONTAL):
                self.count_bomb(i,j)
        #print(self.board)
        
        self.is_exploded = False
        self.is_completed = False
        self.running = True
        
    ###描画
    def draw_board(self):
        screen.fill(CHARCOAL)
        number_font = pygame.font.SysFont("arialblack", 30) # フォントの読み込みと作成
        bomb_img = pygame.image.load("bomb.png")
        bomb_img = pygame.transform.scale(bomb_img, (GRID_SIZE, GRID_SIZE))
        buf = 3
        self.is_completed = True
        self.is_exploded = False
        for i in range(VERTICAL):
            for j in range(HORIZONTAL):
                num = self.board[i,j]
                rect_num = pygame.Rect(j*GRID_SIZE, i*GRID_SIZE, GRID_SIZE, GRID_SIZE)
                rect_mask = pygame.Rect(j*GRID_SIZE+buf, i*GRID_SIZE+buf, GRID_SIZE-2*buf, GRID_SIZE-2*buf)
                pygame.draw.rect(screen, BLACK, rect_num, 1)
                if self.is_opened[i,j]:    #マスク
                    if num > 0: #数字の描画
                        text = number_font.render(str(num), True, (0, 0, 255))  # 描画するテキストの作成
                        text_pos = text.get_rect(center = ((j+0.5)*GRID_SIZE, (i+0.5)*GRID_SIZE))      # 表示位置
                        screen.blit(text, text_pos)                             # 作成したテキストの描画
                    elif num < 0: #爆弾の描画
                        bomb_pos = bomb_img.get_rect(center = ((j+0.5)*GRID_SIZE, (i+0.5)*GRID_SIZE))
                        screen.blit(bomb_img, bomb_pos)
                        self.is_exploded = True
                else:
                    pygame.draw.rect(screen, GRAY, rect_mask, 0)
                    if num >= 0:
                        self.is_completed = False

    ###爆弾設置(-1)
    def set_bomb(self):
        lbom = []
        random.seed(time.time())
        while (len(lbom)<BOM_NUM):
            p = random.randrange(VERTICAL)
            q = random.randrange(HORIZONTAL)
            if not p*VERTICAL+q in lbom:
                lbom.append(p*VERTICAL+q)
                self.board[p,q] = -1
                
    ###爆弾の個数を計算
    def count_bomb(self, i, j):
        if self.board[i,j] != -1:
            cnt = 0
            for k in range(max(0,i-1),min(VERTICAL,i+2)):
                for l in range(max(0,j-1),min(HORIZONTAL,j+2)):
                    if self.board[k,l] == -1:
                        cnt += 1
            self.board[i,j] = cnt

    ###ゼロのとき隣接するゼロもあける再帰
    def search_zero(self, i, j):
        if self.board[i,j] == 0:
            for k in range(max(0,i-1),min(VERTICAL,i+2)):
                for l in range(max(0,j-1),min(HORIZONTAL,j+2)):
                    if self.is_opened[k,l]==False:
                        self.is_opened[k,l] = True
                        self.search_zero(k, l)
        return
    
    ###クリックされた一手の処理
    def next_move(self, i, j):
        if self.is_opened[i,j] == False:
            self.is_opened[i,j] = True
            self.search_zero(i,j)
            
    ###爆破
    async def explode(self):                
        text_font = pygame.font.SysFont("arialblack", 50)
        text = text_font.render("GAME OVER", True, RED)
        text_pos = text.get_rect()
        text_pos.center = screen.get_rect().center
        screen.blit(text, text_pos)
        pygame.display.flip()
        await asyncio.sleep(3)
        self.running = False
        
    ###ゲームクリア
    async def clear(self):
        text_font = pygame.font.SysFont("arialblack", 50)
        text = text_font.render("CLEAR!!", True, YELLOW)
        text_pos = text.get_rect()
        text_pos.center = screen.get_rect().center
        screen.blit(text, text_pos)
        pygame.display.flip()
        await asyncio.sleep(3)
        self.running = False

async def main():
    game = MineSweeper()
    game.draw_board()
    first_click_skipped = False #初回クリックを無視
    
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not first_click_skipped:
                    first_click_skipped = True
                    continue
                x,y = event.pos
                x //= GRID_SIZE
                y //= GRID_SIZE
                game.next_move(y, x)
                game.draw_board()  

        if game.is_exploded:
            await game.explode()
        elif game.is_completed:
            await game.clear()
        pygame.display.flip()
        await asyncio.sleep(0)
    
    #pygame.quit()
    #sys.exit()
    
if __name__ == "__main__":
    asyncio.run(main())