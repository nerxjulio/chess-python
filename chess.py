"""
Chess Pro — Full rules + Strong AI (Minimax + Alpha-Beta) + Themes + Undo + Hints
Install: sudo apt install python3-pygame   OR   pip install pygame --break-system-packages
Run:     python3 chess2.py
"""

import pygame, sys, time, threading
from copy import deepcopy
from functools import lru_cache

# ═══════════════════════════════════════════════════════════════════════════════
#  THEMES
# ═══════════════════════════════════════════════════════════════════════════════
THEMES = {
    "Classique": {
        "light": (240,217,181), "dark": (181,136,99),
        "panel_bg": (28,26,22), "panel2": (44,40,34),
        "accent": (200,160,60), "text": (230,225,210), "text_dim": (130,120,100),
        "btn": (55,50,42), "btn_hov": (75,68,56),
        "piece_w": (255,248,220), "piece_b": (35,28,18),
        "piece_w_out": (160,120,50), "piece_b_out": (80,60,20),
        "hl": (247,247,105,170), "legal": (80,200,80,140), "check": (220,50,50,180),
        "hint_best": (50,200,255,200), "hint_good": (50,255,150,150),
        "coord": (120,90,60),
    },
    "Obsidian": {
        "light": (80,90,100), "dark": (35,40,50),
        "panel_bg": (15,15,22), "panel2": (25,25,36),
        "accent": (100,180,255), "text": (200,215,235), "text_dim": (100,115,135),
        "btn": (30,35,50), "btn_hov": (45,52,72),
        "piece_w": (220,235,255), "piece_b": (30,40,60),
        "piece_w_out": (80,140,220), "piece_b_out": (20,30,50),
        "hl": (100,180,255,160), "legal": (80,255,180,140), "check": (255,80,80,180),
        "hint_best": (255,220,50,210), "hint_good": (255,160,50,150),
        "coord": (80,100,130),
    },
    "Émeraude": {
        "light": (180,210,170), "dark": (80,130,90),
        "panel_bg": (18,28,20), "panel2": (28,44,32),
        "accent": (120,220,100), "text": (210,235,200), "text_dim": (110,150,100),
        "btn": (30,50,35), "btn_hov": (45,72,52),
        "piece_w": (235,255,230), "piece_b": (20,45,25),
        "piece_w_out": (80,160,70), "piece_b_out": (15,40,18),
        "hl": (180,255,100,160), "legal": (100,255,120,140), "check": (255,80,60,180),
        "hint_best": (255,240,60,200), "hint_good": (255,180,60,150),
        "coord": (80,130,70),
    },
    "Rubis": {
        "light": (220,190,190), "dark": (150,80,80),
        "panel_bg": (28,15,15), "panel2": (44,25,25),
        "accent": (240,100,100), "text": (240,210,210), "text_dim": (150,110,110),
        "btn": (55,30,30), "btn_hov": (78,45,45),
        "piece_w": (255,240,240), "piece_b": (45,18,18),
        "piece_w_out": (200,100,80), "piece_b_out": (80,25,25),
        "hl": (255,180,100,160), "legal": (255,100,100,140), "check": (255,40,40,200),
        "hint_best": (80,220,255,200), "hint_good": (80,180,255,150),
        "coord": (150,90,80),
    },
    "Ivoire": {
        "light": (245,240,225), "dark": (195,175,135),
        "panel_bg": (245,240,230), "panel2": (225,215,195),
        "accent": (140,100,50), "text": (60,50,35), "text_dim": (130,115,90),
        "btn": (215,205,185), "btn_hov": (200,188,165),
        "piece_w": (255,252,245), "piece_b": (45,38,28),
        "piece_w_out": (160,130,80), "piece_b_out": (100,80,45),
        "hl": (220,200,80,170), "legal": (80,180,80,130), "check": (210,50,50,170),
        "hint_best": (50,160,220,190), "hint_good": (50,200,120,140),
        "coord": (140,115,80),
    },
}
THEME_NAMES = list(THEMES.keys())

# ═══════════════════════════════════════════════════════════════════════════════
#  PIECE STYLES
# ═══════════════════════════════════════════════════════════════════════════════
PIECE_CHARS_FILLED = {
    'wK':'♔','wQ':'♕','wR':'♖','wB':'♗','wN':'♘','wP':'♙',
    'bK':'♚','bQ':'♛','bR':'♜','bB':'♝','bN':'♞','bP':'♟',
}
# Alternative styles for pieces
PIECE_STYLES = ["Symboles", "Lettres", "Mini"]
PIECE_LABEL = {
    'K':'Roi','Q':'Dame','R':'Tour','B':'Fou','N':'Cavalier','P':'Pion'
}
PIECE_LETTER = {'K':'K','Q':'Q','R':'R','B':'F','N':'C','P':'P'}

# ═══════════════════════════════════════════════════════════════════════════════
#  PIECE SQUARE TABLES (for AI evaluation)
# ═══════════════════════════════════════════════════════════════════════════════
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
   50, 50, 50, 50, 50, 50, 50, 50,
   10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_TABLE = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_TABLE = [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5, 10, 10,  5,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0,
]
QUEEN_TABLE = [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20,
]
KING_MID_TABLE = [
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20,
]
PIECE_VALUES = {'P':100,'N':320,'B':330,'R':500,'Q':900,'K':20000}
PST = {'P':PAWN_TABLE,'N':KNIGHT_TABLE,'B':BISHOP_TABLE,'R':ROOK_TABLE,'Q':QUEEN_TABLE,'K':KING_MID_TABLE}

# ═══════════════════════════════════════════════════════════════════════════════
#  BOARD LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def start_board():
    b=[[None]*8 for _ in range(8)]
    order=['R','N','B','Q','K','B','N','R']
    for c,p in enumerate(order):
        b[0][c]='b'+p; b[7][c]='w'+p
    for c in range(8):
        b[1][c]='bP'; b[6][c]='wP'
    return b

col_of = lambda p: p[0] if p else None
kind_of= lambda p: p[1] if p else None
opp    = lambda c: 'b' if c=='w' else 'w'

def raw_moves(board,r,c,ep,cr):
    p=board[r][c]
    if not p: return []
    col,kind=p[0],p[1]; moves=[]
    def add(tr,tc):
        if 0<=tr<8 and 0<=tc<8:
            t=board[tr][tc]
            if not t or col_of(t)!=col: moves.append((tr,tc))
    def slide(dr,dc):
        tr,tc=r+dr,c+dc
        while 0<=tr<8 and 0<=tc<8:
            t=board[tr][tc]
            if t:
                if col_of(t)!=col: moves.append((tr,tc))
                break
            moves.append((tr,tc)); tr+=dr; tc+=dc
    if kind=='P':
        d=-1 if col=='w' else 1
        if 0<=r+d<8 and not board[r+d][c]:
            moves.append((r+d,c))
            sr=6 if col=='w' else 1
            if r==sr and not board[r+2*d][c]: moves.append((r+2*d,c))
        for dc in(-1,1):
            tr,tc=r+d,c+dc
            if 0<=tr<8 and 0<=tc<8:
                t=board[tr][tc]
                if (t and col_of(t)!=col) or (ep and (tr,tc)==ep): moves.append((tr,tc))
    elif kind=='N':
        for dr,dc in[(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]: add(r+dr,c+dc)
    elif kind=='B':
        for dr,dc in[(-1,-1),(-1,1),(1,-1),(1,1)]: slide(dr,dc)
    elif kind=='R':
        for dr,dc in[(-1,0),(1,0),(0,-1),(0,1)]: slide(dr,dc)
    elif kind=='Q':
        for dr,dc in[(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)]: slide(dr,dc)
    elif kind=='K':
        for dr,dc in[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]: add(r+dr,c+dc)
        row=7 if col=='w' else 0
        if r==row and c==4:
            if cr[col]['K'] and not board[row][5] and not board[row][6]:
                if not sq_attacked(board,row,4,opp(col)) and not sq_attacked(board,row,5,opp(col)) and not sq_attacked(board,row,6,opp(col)):
                    moves.append((row,6))
            if cr[col]['Q'] and not board[row][3] and not board[row][2] and not board[row][1]:
                if not sq_attacked(board,row,4,opp(col)) and not sq_attacked(board,row,3,opp(col)) and not sq_attacked(board,row,2,opp(col)):
                    moves.append((row,2))
    return moves

_no_cr={'w':{'K':False,'Q':False},'b':{'K':False,'Q':False}}
def sq_attacked(board,r,c,by):
    for sr in range(8):
        for sc in range(8):
            p=board[sr][sc]
            if p and col_of(p)==by:
                if (r,c) in raw_moves(board,sr,sc,None,_no_cr): return True
    return False

def king_pos(board,col):
    for r in range(8):
        for c in range(8):
            if board[r][c]==col+'K': return r,c

def in_check(board,col):
    kp=king_pos(board,col)
    return kp and sq_attacked(board,kp[0],kp[1],opp(col))

def apply_move(board,fr,fc,tr,tc,ep,cr,promote='Q'):
    nb=[row[:] for row in board]
    p=nb[fr][fc]; col,kind=p[0],p[1]
    if kind=='P' and ep==(tr,tc): nb[fr][tc]=None
    nb[tr][tc]=p; nb[fr][fc]=None
    if kind=='P' and (tr==0 or tr==7): nb[tr][tc]=col+promote
    if kind=='K':
        row=7 if col=='w' else 0
        if fc==4 and tc==6: nb[row][5]=nb[row][7]; nb[row][7]=None
        elif fc==4 and tc==2: nb[row][3]=nb[row][0]; nb[row][0]=None
    return nb

def upd_cr(cr,piece,fr,fc,board,tr,tc):
    r=deepcopy(cr); col,kind=piece[0],piece[1]
    if kind=='K': r[col]['K']=False; r[col]['Q']=False
    elif kind=='R':
        row=7 if col=='w' else 0
        if fr==row and fc==7: r[col]['K']=False
        if fr==row and fc==0: r[col]['Q']=False
    # if rook captured
    cap=board[tr][tc]
    if cap and kind_of(cap)=='R':
        cc=col_of(cap); row=7 if cc=='w' else 0
        if tr==row and tc==7: r[cc]['K']=False
        if tr==row and tc==0: r[cc]['Q']=False
    return r

def legal_moves(board,r,c,ep,cr):
    p=board[r][c]
    if not p: return []
    col=col_of(p); res=[]
    for tr,tc in raw_moves(board,r,c,ep,cr):
        nb=apply_move(board,r,c,tr,tc,ep,cr)
        if not in_check(nb,col): res.append((tr,tc))
    return res

def all_legal(board,col,ep,cr):
    moves=[]
    for r in range(8):
        for c in range(8):
            if col_of(board[r][c])==col:
                for tr,tc in legal_moves(board,r,c,ep,cr):
                    moves.append((r,c,tr,tc))
    return moves

# ═══════════════════════════════════════════════════════════════════════════════
#  AI — Minimax + Alpha-Beta + Quiescence
# ═══════════════════════════════════════════════════════════════════════════════
def evaluate(board):
    score=0
    for r in range(8):
        for c in range(8):
            p=board[r][c]
            if not p: continue
            col,kind=p[0],p[1]
            val=PIECE_VALUES[kind]
            idx=r*8+c if col=='b' else (7-r)*8+c
            pst=PST[kind][idx]
            s=val+pst
            score += s if col=='w' else -s
    return score

def order_moves(board,moves,ep,cr,maximizing):
    """MVV-LVA ordering: captures first, then promotions."""
    def score(m):
        fr,fc,tr,tc=m
        attacker=board[fr][fc]
        victim=board[tr][tc]
        s=0
        if victim: s=PIECE_VALUES[kind_of(victim)]*10-PIECE_VALUES[kind_of(attacker)]
        if kind_of(attacker)=='P' and (tr==0 or tr==7): s+=800
        return s
    return sorted(moves,key=score,reverse=True)

def minimax(board,depth,alpha,beta,maximizing,ep,cr,start_time,time_limit):
    if time.time()-start_time>time_limit: return evaluate(board),None
    col='w' if maximizing else 'b'
    moves=all_legal(board,col,ep,cr)
    if not moves:
        if in_check(board,col): return (-30000 if maximizing else 30000),None
        return 0,None
    if depth==0: return evaluate(board),None
    moves=order_moves(board,moves,ep,cr,maximizing)
    best_move=None
    best_val=-99999 if maximizing else 99999
    for fr,fc,tr,tc in moves:
        p=board[fr][fc]
        nb=apply_move(board,fr,fc,tr,tc,ep,cr)
        new_ep=None
        if kind_of(p)=='P' and abs(tr-fr)==2: new_ep=((fr+tr)//2,tc)
        new_cr=upd_cr(cr,p,fr,fc,board,tr,tc)
        val,_=minimax(nb,depth-1,alpha,beta,not maximizing,new_ep,new_cr,start_time,time_limit)
        if maximizing:
            if val>best_val: best_val=val; best_move=(fr,fc,tr,tc)
            alpha=max(alpha,val)
        else:
            if val<best_val: best_val=val; best_move=(fr,fc,tr,tc)
            beta=min(beta,val)
        if beta<=alpha: break
    return best_val,best_move

def get_best_moves(board,col,ep,cr,top_n=3):
    """Return top N moves sorted by evaluation (for hint mode)."""
    moves=all_legal(board,col,ep,cr)
    if not moves: return []
    scored=[]
    for fr,fc,tr,tc in moves:
        p=board[fr][fc]
        nb=apply_move(board,fr,fc,tr,tc,ep,cr)
        new_ep=None
        if kind_of(p)=='P' and abs(tr-fr)==2: new_ep=((fr+tr)//2,tc)
        new_cr=upd_cr(cr,p,fr,fc,board,tr,tc)
        # quick 2-ply eval
        val,_=minimax(nb,2,-99999,99999,col=='b',new_ep,new_cr,time.time(),5.0)
        scored.append(((fr,fc,tr,tc),val))
    scored.sort(key=lambda x:x[1],reverse=(col=='w'))
    return [m for m,_ in scored[:top_n]]

# ═══════════════════════════════════════════════════════════════════════════════
#  GAME STATE
# ═══════════════════════════════════════════════════════════════════════════════
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board=start_board()
        self.turn='w'
        self.ep=None
        self.cr=deepcopy({'w':{'K':True,'Q':True},'b':{'K':True,'Q':True}})
        self.selected=None
        self.legal=[]
        self.status='playing'
        self.history=[]        # move strings
        self.undo_stack=[]     # snapshots for undo
        self.promotion_pending=None
        self.flip=False
        self.mode='pvp'        # 'pvp' or 'vs_ai'
        self.ai_color='b'
        self.ai_thinking=False
        self.ai_result=None    # set by ai thread
        self.hint_mode=False
        self.hints=[]          # list of (fr,fc,tr,tc)
        self.hint_computing=False
        self.theme_idx=0
        self.piece_style_idx=0
        self.ai_depth=4        # default strong

    def theme(self): return THEMES[THEME_NAMES[self.theme_idx]]
    def piece_style(self): return PIECE_STYLES[self.piece_style_idx]

    def save_snapshot(self):
        self.undo_stack.append({
            'board':[r[:] for r in self.board],
            'turn':self.turn,'ep':self.ep,
            'cr':deepcopy(self.cr),
            'status':self.status,
            'history':self.history[:],
            'hints':self.hints[:],
        })

    def undo(self):
        if not self.undo_stack: return
        if self.mode=='vs_ai' and len(self.undo_stack)>=2:
            # undo 2 plies (player + AI move)
            self.undo_stack.pop()
        s=self.undo_stack.pop()
        self.board=s['board']; self.turn=s['turn']; self.ep=s['ep']
        self.cr=s['cr']; self.status=s['status']; self.history=s['history']
        self.hints=[]; self.selected=None; self.legal=[]
        self.ai_result=None; self.ai_thinking=False

    def do_move(self,fr,fc,tr,tc,promote='Q'):
        self.save_snapshot()
        p=self.board[fr][fc]
        files='abcdefgh'; ranks='87654321'
        note=f"{'●' if self.turn=='w' else '○'} {PIECE_CHARS_FILLED[p]} {files[fc]}{ranks[fr]}→{files[tc]}{ranks[tr]}"
        new_ep=None
        if kind_of(p)=='P' and abs(tr-fr)==2: new_ep=((fr+tr)//2,tc)
        self.cr=upd_cr(self.cr,p,fr,fc,self.board,tr,tc)
        self.board=apply_move(self.board,fr,fc,tr,tc,self.ep,self.cr,promote)
        self.ep=new_ep
        self.history.append(note)
        if len(self.history)>40: self.history=self.history[-40:]
        self.turn=opp(self.turn)
        self.selected=None; self.legal=[]; self.hints=[]
        self._update_status()

    def _update_status(self):
        ic=in_check(self.board,self.turn)
        hm=bool(all_legal(self.board,self.turn,self.ep,self.cr))
        if not hm: self.status='checkmate' if ic else 'stalemate'
        elif ic:   self.status='check'
        else:      self.status='playing'

    def click(self,r,c):
        if self.status in('checkmate','stalemate'): return
        if self.promotion_pending: return
        if self.ai_thinking: return
        if self.mode=='vs_ai' and self.turn==self.ai_color: return
        p=self.board[r][c]
        if self.selected:
            fr,fc=self.selected
            if (r,c) in self.legal:
                piece=self.board[fr][fc]
                if kind_of(piece)=='P' and (r==0 or r==7):
                    self.promotion_pending=(fr,fc,r,c)
                else:
                    self.do_move(fr,fc,r,c)
                return
            self.selected=None; self.legal=[]
        if p and col_of(p)==self.turn:
            self.selected=(r,c)
            self.legal=legal_moves(self.board,r,c,self.ep,self.cr)

    def promote(self,kind):
        if not self.promotion_pending: return
        fr,fc,tr,tc=self.promotion_pending
        self.promotion_pending=None
        self.do_move(fr,fc,tr,tc,promote=kind)

    def start_ai_move(self):
        if self.ai_thinking: return
        self.ai_thinking=True
        def run():
            t=time.time()
            tl=3.0  # 3 sec time limit
            _,move=minimax(self.board,self.ai_depth,-99999,99999,
                           self.ai_color=='w',self.ep,self.cr,t,tl)
            self.ai_result=move
        threading.Thread(target=run,daemon=True).start()

    def start_hint(self):
        if self.hint_computing: return
        self.hint_computing=True
        def run():
            h=get_best_moves(self.board,self.turn,self.ep,self.cr,top_n=3)
            self.hints=h; self.hint_computing=False
        threading.Thread(target=run,daemon=True).start()

    def col_name(self,col): return 'Blancs' if col=='w' else 'Noirs'

# ═══════════════════════════════════════════════════════════════════════════════
#  RENDERING
# ═══════════════════════════════════════════════════════════════════════════════
BOARD_SIZE=720; PANEL_W=280; W=BOARD_SIZE+PANEL_W; H=BOARD_SIZE; SQ=BOARD_SIZE//8

class Renderer:
    def __init__(self,screen):
        self.screen=screen
        self._init_fonts()
        self.board_surf=pygame.Surface((BOARD_SIZE,BOARD_SIZE))
        self.overlay=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
        self.panel=pygame.Surface((PANEL_W,H))
        self._anim_t=0

    def _init_fonts(self):
        def sf(size,bold=False):
            for n in ['Georgia','Times New Roman','DejaVu Serif','FreeSerif','serif']:
                try: f=pygame.font.SysFont(n,size,bold=bold)
                except: continue
                if f: return f
            return pygame.font.Font(None,size)
        def sym(size):
            for n in ['Segoe UI Symbol','Symbola','DejaVu Sans','Noto Sans Symbols','FreeSerif']:
                try: f=pygame.font.SysFont(n,size)
                except: continue
                if f: return f
            return pygame.font.Font(None,size)
        self.fL=sf(26,True); self.fM=sf(17,True); self.fS=sf(13)
        self.fXS=sf(11); self.fSym=sym(SQ-6); self.fSymB=sym(SQ)
        self.fSymS=sym(SQ-18)

    def sq_to_px(self,r,c,flip):
        dr=7-r if flip else r; dc=7-c if flip else c
        return dc*SQ,dr*SQ

    def draw(self,game,dt):
        self._anim_t+=dt
        T=game.theme()
        self.screen.fill(T['panel_bg'])
        self._draw_board(game,T)
        self._draw_panel(game,T)
        if game.promotion_pending:
            self._draw_promotion(game,T)

    def _draw_board(self,game,T):
        flip=game.flip
        # squares
        for r in range(8):
            for c in range(8):
                x,y=self.sq_to_px(r,c,flip)
                col=T['light'] if (r+c)%2==0 else T['dark']
                pygame.draw.rect(self.board_surf,col,(x,y,SQ,SQ))

        # hint arrows (best moves)
        for i,(fr,fc,tr,tc) in enumerate(game.hints):
            x1,y1=self.sq_to_px(fr,fc,flip); x1+=SQ//2; y1+=SQ//2
            x2,y2=self.sq_to_px(tr,tc,flip); x2+=SQ//2; y2+=SQ//2
            hcol=T['hint_best'] if i==0 else T['hint_good']
            self._draw_arrow(x1,y1,x2,y2,hcol)
            # highlight destination
            ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
            ov.fill((*hcol[:3],80))
            self.board_surf.blit(ov,self.sq_to_px(tr,tc,flip))

        # selected highlight
        if game.selected:
            sr,sc=game.selected; x,y=self.sq_to_px(sr,sc,flip)
            ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
            ov.fill(T['hl']); self.board_surf.blit(ov,(x,y))

        # legal moves
        for tr,tc in game.legal:
            x,y=self.sq_to_px(tr,tc,flip)
            ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
            if game.board[tr][tc]:
                pygame.draw.rect(ov,T['legal'],(0,0,SQ,SQ),5)
            else:
                pygame.draw.circle(ov,T['legal'],(SQ//2,SQ//2),SQ//7)
            self.board_surf.blit(ov,(x,y))

        # check highlight
        if game.status in('check','checkmate'):
            kp=king_pos(game.board,game.turn)
            if kp:
                x,y=self.sq_to_px(kp[0],kp[1],flip)
                ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
                # pulsing effect
                alpha=int(120+80*abs(__import__('math').sin(self._anim_t*3)))
                ov.fill((*T['check'][:3],alpha))
                self.board_surf.blit(ov,(x,y))

        # coordinates
        files='abcdefgh'; ranks='87654321'
        for i in range(8):
            lf=self.fXS.render(files[i] if not flip else files[7-i],True,T['coord'])
            self.board_surf.blit(lf,(i*SQ+SQ-13,BOARD_SIZE-13))
            lr=self.fXS.render(ranks[i] if not flip else ranks[7-i],True,T['coord'])
            self.board_surf.blit(lr,(3,i*SQ+3))

        # pieces
        for r in range(8):
            for c in range(8):
                p=game.board[r][c]
                if p:
                    x,y=self.sq_to_px(r,c,flip)
                    self._draw_piece(p,x,y,game.piece_style(),T)

        self.screen.blit(self.board_surf,(0,0))
        # board border
        pygame.draw.rect(self.screen,T['accent'],(0,0,BOARD_SIZE,BOARD_SIZE),2)

    def _draw_arrow(self,x1,y1,x2,y2,color):
        import math
        rgb=color[:3]; a=color[3] if len(color)>3 else 200
        surf=pygame.Surface((BOARD_SIZE,BOARD_SIZE),pygame.SRCALPHA)
        lw=6
        pygame.draw.line(surf,(*rgb,a),(x1,y1),(x2,y2),lw)
        ang=math.atan2(y2-y1,x2-x1)
        al=18; aa=0.5
        ax1=x2-al*math.cos(ang-aa); ay1=y2-al*math.sin(ang-aa)
        ax2=x2-al*math.cos(ang+aa); ay2=y2-al*math.sin(ang+aa)
        pygame.draw.polygon(surf,(*rgb,a),[(x2,y2),(ax1,ay1),(ax2,ay2)])
        self.board_surf.blit(surf,(0,0))

    def _draw_piece(self,p,x,y,style,T):
        col=col_of(p); kind=kind_of(p)
        wc=T['piece_w'] if col=='w' else T['piece_b']
        oc=T['piece_w_out'] if col=='w' else T['piece_b_out']
        if style=='Symboles':
            sym=PIECE_CHARS_FILLED[p]
            # shadow
            sh=self.fSym.render(sym,True,(0,0,0))
            self.board_surf.blit(sh,(x+SQ//2-sh.get_width()//2+2,y+SQ//2-sh.get_height()//2+2))
            # outline
            for dx,dy in[(-1,0),(1,0),(0,-1),(0,1)]:
                ol=self.fSym.render(sym,True,oc)
                self.board_surf.blit(ol,(x+SQ//2-ol.get_width()//2+dx,y+SQ//2-ol.get_height()//2+dy))
            lbl=self.fSym.render(sym,True,wc)
            self.board_surf.blit(lbl,(x+SQ//2-lbl.get_width()//2,y+SQ//2-lbl.get_height()//2))
        elif style=='Lettres':
            letter=PIECE_LETTER[kind]
            # draw circle background
            pygame.draw.circle(self.board_surf,oc,(x+SQ//2,y+SQ//2),SQ//2-6)
            pygame.draw.circle(self.board_surf,wc,(x+SQ//2,y+SQ//2),SQ//2-8)
            lbl=self.fM.render(letter,True,oc)
            self.board_surf.blit(lbl,(x+SQ//2-lbl.get_width()//2,y+SQ//2-lbl.get_height()//2))
        elif style=='Mini':
            sym=PIECE_CHARS_FILLED[p]
            pygame.draw.circle(self.board_surf,oc,(x+SQ//2,y+SQ//2),SQ//2-4)
            pygame.draw.circle(self.board_surf,wc,(x+SQ//2,y+SQ//2),SQ//2-6)
            lbl=self.fSymS.render(sym,True,oc)
            self.board_surf.blit(lbl,(x+SQ//2-lbl.get_width()//2,y+SQ//2-lbl.get_height()//2))

    def _draw_panel(self,game,T):
        self.panel.fill(T['panel_bg'])
        x0=14; pw=PANEL_W-2*x0; y=12

        # Title
        t=self.fL.render("♟ ÉCHECS PRO",True,T['accent'])
        self.panel.blit(t,(x0,y)); y+=36

        # Status
        if game.status=='checkmate':
            msg=f"Échec et mat!"; sub=f"{game.col_name(opp(game.turn))} gagne 🏆"; sc=(220,60,60)
        elif game.status=='stalemate':
            msg="Pat!"; sub="Match nul"; sc=(200,200,60)
        elif game.status=='check':
            msg="ÉCHEC AU ROI!"; sub=game.col_name(game.turn); sc=(230,100,40)
        elif game.ai_thinking:
            dots="."*(1+int(self._anim_t*2)%4)
            msg=f"IA réfléchit{dots}"; sub=""; sc=T['text_dim']
        elif game.hint_computing:
            msg="Analyse en cours..."; sub=""; sc=T['text_dim']
        else:
            msg=f"Tour des {game.col_name(game.turn)}"; sub=""; sc=T['text']

        lm=self.fM.render(msg,True,sc)
        self.panel.blit(lm,(x0,y)); y+=22
        if sub:
            ls=self.fS.render(sub,True,T['text_dim'])
            self.panel.blit(ls,(x0,y)); y+=18
        y+=4

        # Mode
        mode_txt="Mode: Joueur vs IA" if game.mode=='vs_ai' else "Mode: 2 Joueurs"
        lmode=self.fXS.render(mode_txt,True,T['text_dim'])
        self.panel.blit(lmode,(x0,y)); y+=14
        if game.mode=='vs_ai':
            lvl=["Facile","Normal","Fort","Expert","Maître"][min(game.ai_depth//1-1,4)]
            ll=self.fXS.render(f"Niveau: {lvl}  |  IA = {game.col_name(game.ai_color)}",True,T['text_dim'])
            self.panel.blit(ll,(x0,y)); y+=14
        y+=2
        pygame.draw.line(self.panel,T['panel2'],(x0,y),(PANEL_W-x0,y),1); y+=8

        # History
        ht=self.fS.render("Historique",True,T['accent']); self.panel.blit(ht,(x0,y)); y+=18
        max_entries=12
        for entry in game.history[-max_entries:]:
            wc=T['text'] if entry.startswith('●') else T['text_dim']
            le=self.fXS.render(entry,True,wc)
            self.panel.blit(le,(x0,y)); y+=15

        # Buttons — bottom section
        self._buttons_layout={}
        by=H-320
        def btn(label,key,yy):
            rect=pygame.Rect(x0,yy,pw,32)
            self._buttons_layout[key]=pygame.Rect(BOARD_SIZE+x0,yy,pw,32)
            mx,my=pygame.mouse.get_pos(); mx-=BOARD_SIZE
            hov=rect.collidepoint(mx,my)
            bc=T['btn_hov'] if hov else T['btn']
            pygame.draw.rect(self.panel,bc,rect,border_radius=6)
            pygame.draw.rect(self.panel,T['accent'],rect,1,border_radius=6)
            lb=self.fS.render(label,True,T['text'])
            self.panel.blit(lb,(x0+pw//2-lb.get_width()//2,yy+16-lb.get_height()//2))
            return yy+38

        by=btn("🔄 Nouvelle Partie",'new',by)
        by=btn("↩ Annuler le coup",'undo',by)
        by=btn("💡 Meilleurs coups",'hint',by)
        # Hint mode toggle
        hint_lbl=f"Mode Hint: {'ON ✓' if game.hint_mode else 'OFF'}"
        by=btn(hint_lbl,'hint_mode',by)
        by=btn("🔁 Retourner",'flip',by)
        by+=4
        pygame.draw.line(self.panel,T['panel2'],(x0,by),(PANEL_W-x0,by),1); by+=6

        # Theme selector
        tl=self.fXS.render("Thème:",True,T['accent']); self.panel.blit(tl,(x0,by)); by+=16
        for i,tn in enumerate(THEME_NAMES):
            r=pygame.Rect(x0+(i%3)*(pw//3),by+(i//3)*22,pw//3-2,18)
            self._buttons_layout[f'theme_{i}']=pygame.Rect(BOARD_SIZE+r.x,r.y,r.w,r.h)
            sel=i==game.theme_idx
            bc=T['accent'] if sel else T['btn']
            pygame.draw.rect(self.panel,bc,r,border_radius=4)
            lb=self.fXS.render(tn,True,T['panel_bg'] if sel else T['text'])
            self.panel.blit(lb,(r.x+r.w//2-lb.get_width()//2,r.y+9-lb.get_height()//2))
        by+=44+6

        # Piece style
        pl=self.fXS.render("Style pièces:",True,T['accent']); self.panel.blit(pl,(x0,by)); by+=16
        for i,ps in enumerate(PIECE_STYLES):
            r=pygame.Rect(x0+i*(pw//3),by,pw//3-2,18)
            self._buttons_layout[f'pstyle_{i}']=pygame.Rect(BOARD_SIZE+r.x,r.y,r.w,r.h)
            sel=i==game.piece_style_idx
            bc=T['accent'] if sel else T['btn']
            pygame.draw.rect(self.panel,bc,r,border_radius=4)
            lb=self.fXS.render(ps,True,T['panel_bg'] if sel else T['text'])
            self.panel.blit(lb,(r.x+r.w//2-lb.get_width()//2,r.y+9-lb.get_height()//2))
        by+=24

        # Mode vs AI selector
        pygame.draw.line(self.panel,T['panel2'],(x0,by),(PANEL_W-x0,by),1); by+=6
        ml=self.fXS.render("Mode de jeu:",True,T['accent']); self.panel.blit(ml,(x0,by)); by+=16
        for i,(lbl,key) in enumerate([("2 Joueurs",'pvp'),("vs IA",'ai')]):
            r=pygame.Rect(x0+i*(pw//2),by,pw//2-2,18)
            self._buttons_layout[f'mode_{key}']=pygame.Rect(BOARD_SIZE+r.x,r.y,r.w,r.h)
            sel=(game.mode=='pvp' and key=='pvp') or (game.mode=='vs_ai' and key=='ai')
            bc=T['accent'] if sel else T['btn']
            pygame.draw.rect(self.panel,bc,r,border_radius=4)
            lb=self.fXS.render(lbl,True,T['panel_bg'] if sel else T['text'])
            self.panel.blit(lb,(r.x+r.w//2-lb.get_width()//2,r.y+9-lb.get_height()//2))
        by+=24

        # Difficulty
        dl=self.fXS.render("Difficulté:",True,T['accent']); self.panel.blit(dl,(x0,by)); by+=16
        diff_labels=["Facile","Normal","Fort","Expert","Maître"]
        diff_depths=[2,3,4,5,6]
        n=len(diff_labels); bw2=pw//n
        for i,(lbl,dep) in enumerate(zip(diff_labels,diff_depths)):
            r=pygame.Rect(x0+i*bw2,by,bw2-2,18)
            self._buttons_layout[f'diff_{i}']=pygame.Rect(BOARD_SIZE+r.x,r.y,r.w,r.h)
            sel=game.ai_depth==dep
            bc=T['accent'] if sel else T['btn']
            pygame.draw.rect(self.panel,bc,r,border_radius=4)
            lb=self.fXS.render(lbl,True,T['panel_bg'] if sel else T['text'])
            self.panel.blit(lb,(r.x+r.w//2-lb.get_width()//2,r.y+9-lb.get_height()//2))

        self.screen.blit(self.panel,(BOARD_SIZE,0))

    def _draw_promotion(self,game,T):
        fr,fc,tr,tc=game.promotion_pending
        col=col_of(game.board[fr][fc])
        choices=['Q','R','B','N']
        pad=10; total=len(choices)*(SQ+pad)-pad
        ox=(BOARD_SIZE-total)//2; oy=(BOARD_SIZE-SQ)//2
        ov=pygame.Surface((BOARD_SIZE,BOARD_SIZE),pygame.SRCALPHA)
        ov.fill((0,0,0,160)); self.screen.blit(ov,(0,0))
        bx=ox-22; bw=total+44; bh=SQ+70
        pygame.draw.rect(self.screen,T['panel_bg'],(bx,oy-36,bw,bh),border_radius=14)
        pygame.draw.rect(self.screen,T['accent'],(bx,oy-36,bw,bh),2,border_radius=14)
        tl=self.fM.render("Choisir la pièce",True,T['text'])
        self.screen.blit(tl,(bx+bw//2-tl.get_width()//2,oy-30))
        self._promo_rects=[]
        for i,k in enumerate(choices):
            rx=ox+i*(SQ+pad); ry=oy+16
            pygame.draw.rect(self.screen,T['btn'],(rx,ry,SQ,SQ),border_radius=8)
            pygame.draw.rect(self.screen,T['panel2'],(rx,ry,SQ,SQ),1,border_radius=8)
            p=col+k; wc=T['piece_w'] if col=='w' else T['piece_b']
            sym=PIECE_CHARS_FILLED[p]
            lb=self.fSymB.render(sym,True,wc)
            self.screen.blit(lb,(rx+SQ//2-lb.get_width()//2,ry+SQ//2-lb.get_height()//2))
            nl=self.fXS.render(PIECE_LABEL[k],True,T['text_dim'])
            self.screen.blit(nl,(rx+SQ//2-nl.get_width()//2,ry+SQ+2))
            self._promo_rects.append((rx,ry,SQ,SQ,k))

    def get_buttons(self): return getattr(self,'_buttons_layout',{})
    def get_promo_rects(self): return getattr(self,'_promo_rects',[])

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    pygame.init()
    screen=pygame.display.set_mode((W,H))
    pygame.display.set_caption("Échecs Pro")
    renderer=Renderer(screen)
    game=Game()
    clock=pygame.time.Clock()
    last_time=time.time()

    # auto-hint in hint_mode
    hint_cooldown=0.0

    while True:
        now=time.time(); dt=now-last_time; last_time=now
        hint_cooldown=max(0,hint_cooldown-dt)

        # AI move handling
        if game.mode=='vs_ai' and game.turn==game.ai_color \
           and not game.ai_thinking and game.status=='playing' and game.ai_result is None:
            game.start_ai_move()
        if game.ai_result is not None and not game.ai_thinking:
            move=game.ai_result; game.ai_result=None
            if move:
                fr,fc,tr,tc=move
                p=game.board[fr][fc]
                if kind_of(p)=='P' and (tr==0 or tr==7):
                    game.save_snapshot()
                    game.board=apply_move(game.board,fr,fc,tr,tc,game.ep,game.cr,'Q')
                    game.cr=upd_cr(game.cr,p,fr,fc,game.board,tr,tc)
                    new_ep=None
                    if abs(tr-fr)==2: new_ep=((fr+tr)//2,tc)
                    game.ep=new_ep
                    files='abcdefgh'; ranks='87654321'
                    note=f"{'●' if game.turn=='w' else '○'} {PIECE_CHARS_FILLED[p]} {files[fc]}{ranks[fr]}→{files[tc]}{ranks[tr]}"
                    game.history.append(note)
                    game.turn=opp(game.turn); game._update_status()
                else:
                    game.do_move(fr,fc,tr,tc)
            game.ai_thinking=False

        # Auto-hint in hint mode
        if game.hint_mode and not game.hints and not game.hint_computing \
           and game.status=='playing' and hint_cooldown<=0:
            game.start_hint(); hint_cooldown=1.0

        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_z and (event.mod & pygame.KMOD_CTRL): game.undo()
                if event.key==pygame.K_h: game.start_hint()
                if event.key==pygame.K_n: game.reset()

            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                mx,my=event.pos

                # promotion
                if game.promotion_pending:
                    for rx,ry,rw,rh,k in renderer.get_promo_rects():
                        if rx<=mx<rx+rw and ry<=my<ry+rh: game.promote(k)
                    continue

                # panel buttons
                btns=renderer.get_buttons()
                clicked=False
                for key,rect in btns.items():
                    if rect.collidepoint(mx,my):
                        clicked=True
                        if key=='new': game.reset()
                        elif key=='undo': game.undo()
                        elif key=='hint': game.start_hint()
                        elif key=='hint_mode':
                            game.hint_mode=not game.hint_mode
                            if not game.hint_mode: game.hints=[]
                        elif key=='flip': game.flip=not game.flip
                        elif key.startswith('theme_'): game.theme_idx=int(key.split('_')[1])
                        elif key.startswith('pstyle_'): game.piece_style_idx=int(key.split('_')[1])
                        elif key=='mode_pvp': game.mode='pvp'
                        elif key=='mode_ai': game.mode='vs_ai'; game.ai_color='b'
                        elif key.startswith('diff_'):
                            deps=[2,3,4,5,6]; game.ai_depth=deps[int(key.split('_')[1])]
                        break
                if clicked: continue

                # board click
                if mx<BOARD_SIZE:
                    c=mx//SQ; r=my//SQ
                    if game.flip: r,c=7-r,7-c
                    game.click(r,c)

        renderer.draw(game,dt)
        pygame.display.flip()
        clock.tick(60)

if __name__=='__main__':
    main()
