"""
Chess Pro — Full rules + Strong AI (Negamax + Alpha-Beta + TT + Quiescence) + Themes +
Undo + Hints + Analysis/Blind/Chrono/Puzzle modes + PGN/FEN + optional Stockfish backend.
Install: sudo apt install python3-pygame   OR   pip install pygame --break-system-packages
Run:     python3 chess.py
"""

import pygame, sys, time, threading, os, json, re, shutil, subprocess, random, math, textwrap, asyncio
from copy import deepcopy

IS_WEB = sys.platform == "emscripten"   # True when running under pygbag in a browser

# ═══════════════════════════════════════════════════════════════════════════════
#  THEMES
# ═══════════════════════════════════════════════════════════════════════════════
THEMES = {
    "Chess.com": {
        "light": (238,238,210), "dark": (118,150,86),
        "panel_bg": (38,36,33), "panel2": (54,51,47),
        "accent": (129,182,76), "text": (237,237,232), "text_dim": (150,146,138),
        "btn": (56,53,49), "btn_hov": (72,68,62),
        "piece_w": (250,250,247), "piece_b": (30,28,25),
        "piece_w_out": (190,190,184), "piece_b_out": (10,10,8),
        "hl": (255,255,90,140), "legal": (20,20,20,55), "check": (235,60,55,190),
        "hint_best": (129,182,76,220), "hint_good": (100,160,220,150),
        "coord": (170,205,140), "graph_line": (129,182,76), "graph_bg": (30,28,25),
    },
    "Classique": {
        "light": (240,217,181), "dark": (181,136,99),
        "panel_bg": (28,26,22), "panel2": (44,40,34),
        "accent": (200,160,60), "text": (230,225,210), "text_dim": (130,120,100),
        "btn": (55,50,42), "btn_hov": (75,68,56),
        "piece_w": (255,248,220), "piece_b": (35,28,18),
        "piece_w_out": (160,120,50), "piece_b_out": (80,60,20),
        "hl": (247,247,105,170), "legal": (80,200,80,140), "check": (220,50,50,180),
        "hint_best": (50,200,255,200), "hint_good": (50,255,150,150),
        "coord": (120,90,60), "graph_line": (200,160,60), "graph_bg": (20,18,15),
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
        "coord": (80,100,130), "graph_line": (100,180,255), "graph_bg": (10,10,16),
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
        "coord": (80,130,70), "graph_line": (120,220,100), "graph_bg": (12,20,14),
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
        "coord": (150,90,80), "graph_line": (240,100,100), "graph_bg": (20,10,10),
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
        "coord": (140,115,80), "graph_line": (140,100,50), "graph_bg": (235,228,212),
    },
}
THEME_NAMES = list(THEMES.keys())
ANALYSIS_GREEN = (40,220,90,220)   # fixed green for the Analysis-mode suggestion arrow (spec: "flèche verte")

# ═══════════════════════════════════════════════════════════════════════════════
#  PIECE STYLES
# ═══════════════════════════════════════════════════════════════════════════════
PIECE_CHARS_FILLED = {
    'wK':'♔','wQ':'♕','wR':'♖','wB':'♗','wN':'♘','wP':'♙',
    'bK':'♚','bQ':'♛','bR':'♜','bB':'♝','bN':'♞','bP':'♟',
}
PIECE_STYLES = ["Symboles", "Lettres", "Mini"]
PIECE_LABEL = {'K':'Roi','Q':'Dame','R':'Tour','B':'Fou','N':'Cavalier','P':'Pion'}
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

FILES = 'abcdefgh'
RANKS = '87654321'   # RANKS[row] gives the FEN/algebraic rank digit for board row `row`

def sq_name(r,c): return FILES[c]+RANKS[r]
def parse_sq(s): return RANKS.index(s[1]), FILES.index(s[0])

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

def is_capture_move(board,fr,fc,tr,tc,ep):
    """True if this move removes an enemy piece (normal capture or en passant)."""
    if board[tr][tc] is not None: return True
    p=board[fr][fc]
    return kind_of(p)=='P' and ep is not None and (tr,tc)==ep

def next_ep(board,fr,fc,tr,tc):
    p=board[fr][fc]
    if kind_of(p)=='P' and abs(tr-fr)==2: return ((fr+tr)//2,tc)
    return None

# ═══════════════════════════════════════════════════════════════════════════════
#  ZOBRIST HASHING (transposition table keys, repetition detection)
# ═══════════════════════════════════════════════════════════════════════════════
_zr=random.Random(20240521)
ZOBRIST_PIECES={col+kind:[_zr.getrandbits(64) for _ in range(64)] for col in 'wb' for kind in 'PNBRQK'}
ZOBRIST_CASTLING={col+side:_zr.getrandbits(64) for col in 'wb' for side in 'KQ'}
ZOBRIST_EP_FILE=[_zr.getrandbits(64) for _ in range(8)]
ZOBRIST_SIDE=_zr.getrandbits(64)

def zobrist_hash(board,turn,ep,cr):
    h=0
    for r in range(8):
        for c in range(8):
            p=board[r][c]
            if p: h^=ZOBRIST_PIECES[p][r*8+c]
    if turn=='b': h^=ZOBRIST_SIDE
    for col in 'wb':
        for side in 'KQ':
            if cr[col][side]: h^=ZOBRIST_CASTLING[col+side]
    if ep: h^=ZOBRIST_EP_FILE[ep[1]]
    return h

# ═══════════════════════════════════════════════════════════════════════════════
#  FEN
# ═══════════════════════════════════════════════════════════════════════════════
START_FEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def board_from_fen(fen):
    parts=fen.strip().split()
    if len(parts)<4: raise ValueError("FEN incomplet (au moins 4 champs requis)")
    placement,active,castling,ep_str=parts[0],parts[1],parts[2],parts[3]
    halfmove=int(parts[4]) if len(parts)>4 else 0
    fullmove=int(parts[5]) if len(parts)>5 else 1
    board=[[None]*8 for _ in range(8)]
    rows=placement.split('/')
    if len(rows)!=8: raise ValueError("FEN invalide : 8 rangées attendues")
    for r,row in enumerate(rows):
        c=0
        for ch in row:
            if ch.isdigit(): c+=int(ch)
            else:
                if c>7: raise ValueError("FEN invalide : rangée trop longue")
                color='w' if ch.isupper() else 'b'
                kind=ch.upper()
                if kind not in PIECE_VALUES: raise ValueError(f"FEN invalide : pièce inconnue '{ch}'")
                board[r][c]=color+kind; c+=1
    turn='w' if active=='w' else 'b'
    cr={'w':{'K':'K' in castling,'Q':'Q' in castling},'b':{'K':'k' in castling,'Q':'q' in castling}}
    ep=None
    if ep_str!='-':
        ep=parse_sq(ep_str)
    return board,turn,cr,ep,halfmove,fullmove

def board_to_fen(board,turn,cr,ep,halfmove,fullmove):
    rows=[]
    for r in range(8):
        row=''; empty=0
        for c in range(8):
            p=board[r][c]
            if not p: empty+=1
            else:
                if empty: row+=str(empty); empty=0
                ch=kind_of(p)
                row+= ch if col_of(p)=='w' else ch.lower()
        if empty: row+=str(empty)
        rows.append(row)
    placement='/'.join(rows)
    castling=''.join([
        'K' if cr['w']['K'] else '', 'Q' if cr['w']['Q'] else '',
        'k' if cr['b']['K'] else '', 'q' if cr['b']['Q'] else '',
    ]) or '-'
    ep_str=sq_name(*ep) if ep else '-'
    return f"{placement} {turn} {castling} {ep_str} {halfmove} {fullmove}"

# ═══════════════════════════════════════════════════════════════════════════════
#  ALGEBRAIC (SAN) NOTATION
# ═══════════════════════════════════════════════════════════════════════════════
def to_san(board,fr,fc,tr,tc,ep,cr,promote,post_board,post_turn,post_ep,post_cr):
    """SAN for a move, computed from the PRE-move board/ep/cr plus the resulting POST-move
       state (needed only to detect +/# suffixes)."""
    piece=board[fr][fc]; kind=kind_of(piece)
    capture=is_capture_move(board,fr,fc,tr,tc,ep)
    if kind=='K' and fc==4 and tc==6: core='O-O'
    elif kind=='K' and fc==4 and tc==2: core='O-O-O'
    elif kind=='P':
        core=(FILES[fc]+'x'+sq_name(tr,tc)) if capture else sq_name(tr,tc)
        if tr==0 or tr==7: core+='='+promote
    else:
        others=[]
        for r2 in range(8):
            for c2 in range(8):
                if (r2,c2)!=(fr,fc) and board[r2][c2]==piece and (tr,tc) in legal_moves(board,r2,c2,ep,cr):
                    others.append((r2,c2))
        disambig=''
        if others:
            same_file=any(c2==fc for r2,c2 in others)
            same_rank=any(r2==fr for r2,c2 in others)
            if not same_file: disambig=FILES[fc]
            elif not same_rank: disambig=RANKS[fr]
            else: disambig=FILES[fc]+RANKS[fr]
        core=kind+disambig+('x' if capture else '')+sq_name(tr,tc)
    if in_check(post_board,post_turn):
        mated = not all_legal(post_board,post_turn,post_ep,post_cr)
        core += '#' if mated else '+'
    return core

def parse_uci_move(uci):
    """'e2e4' or 'e7e8q' -> (fr,fc,tr,tc,promote)."""
    fr,fc=parse_sq(uci[0:2]); tr,tc=parse_sq(uci[2:4])
    promote=uci[4].upper() if len(uci)>4 else 'Q'
    return fr,fc,tr,tc,promote

def to_uci_move(fr,fc,tr,tc,promote=None,is_promo=False):
    s=sq_name(fr,fc)+sq_name(tr,tc)
    if is_promo: s+=(promote or 'Q').lower()
    return s

# ═══════════════════════════════════════════════════════════════════════════════
#  AI — Negamax + Alpha-Beta + Transposition Table + Quiescence + Iterative Deepening
# ═══════════════════════════════════════════════════════════════════════════════
MATE=100000
MATE_THRESHOLD=90000
TT_EXACT,TT_LOWER,TT_UPPER=0,1,2
INF=10**9

class TimeUp(Exception): pass

def evaluate(board):
    """Absolute material+PST score, positive = White is better (in centipawns)."""
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

_CENTER_BONUS=[int(6-2*(abs(r-3.5)+abs(c-3.5))) for r in range(8) for c in range(8)]

def order_moves(board,moves,tt_move):
    def score(m):
        if m==tt_move: return 10_000_000
        fr,fc,tr,tc=m
        attacker=board[fr][fc]; victim=board[tr][tc]
        s=0
        if victim is not None:
            s+=100_000+PIECE_VALUES[kind_of(victim)]*10-PIECE_VALUES[kind_of(attacker)]
        if kind_of(attacker)=='P' and (tr==0 or tr==7): s+=9000
        s+=_CENTER_BONUS[tr*8+tc]
        return s
    return sorted(moves,key=score,reverse=True)

def quiescence(board,alpha,beta,turn,ep,cr,start_time,time_limit,ply,qply=0):
    if time.time()-start_time>time_limit: raise TimeUp()
    check=in_check(board,turn)
    stand_pat=evaluate(board) if turn=='w' else -evaluate(board)
    if not check:
        if stand_pat>=beta: return beta
        if stand_pat>alpha: alpha=stand_pat
    if qply>=6:
        return alpha
    moves=all_legal(board,turn,ep,cr)
    if not moves:
        return -(MATE-ply) if check else 0
    if check:
        candidates=moves
    else:
        candidates=[m for m in moves if is_capture_move(board,m[0],m[1],m[2],m[3],ep)]
    candidates=order_moves(board,candidates,None)
    for fr,fc,tr,tc in candidates:
        p=board[fr][fc]
        nb=apply_move(board,fr,fc,tr,tc,ep,cr)
        new_ep=next_ep(board,fr,fc,tr,tc)
        new_cr=upd_cr(cr,p,fr,fc,board,tr,tc)
        val=-quiescence(nb,-beta,-alpha,opp(turn),new_ep,new_cr,start_time,time_limit,ply+1,qply+1)
        if val>=beta: return beta
        if val>alpha: alpha=val
    return alpha

def negamax(board,depth,alpha,beta,turn,ep,cr,tt,ply,start_time,time_limit):
    if time.time()-start_time>time_limit: raise TimeUp()
    alpha_orig=alpha
    key=zobrist_hash(board,turn,ep,cr)
    entry=tt.get(key)
    tt_move=None
    if entry:
        e_depth,e_val,e_flag,e_move=entry
        tt_move=e_move
        if e_depth>=depth:
            if e_flag==TT_EXACT: return e_val
            elif e_flag==TT_LOWER: alpha=max(alpha,e_val)
            elif e_flag==TT_UPPER: beta=min(beta,e_val)
            if alpha>=beta: return e_val
    moves=all_legal(board,turn,ep,cr)
    if not moves:
        return -(MATE-ply) if in_check(board,turn) else 0
    if depth<=0:
        return quiescence(board,alpha,beta,turn,ep,cr,start_time,time_limit,ply)
    moves=order_moves(board,moves,tt_move)
    best_val=-INF; best_move=None
    for fr,fc,tr,tc in moves:
        p=board[fr][fc]
        nb=apply_move(board,fr,fc,tr,tc,ep,cr)
        new_ep=next_ep(board,fr,fc,tr,tc)
        new_cr=upd_cr(cr,p,fr,fc,board,tr,tc)
        val=-negamax(nb,depth-1,-beta,-alpha,opp(turn),new_ep,new_cr,tt,ply+1,start_time,time_limit)
        if val>best_val: best_val=val; best_move=(fr,fc,tr,tc)
        if val>alpha: alpha=val
        if alpha>=beta: break
    if abs(best_val)<MATE_THRESHOLD and len(tt)<2_000_000:
        flag=TT_EXACT
        if best_val<=alpha_orig: flag=TT_UPPER
        elif best_val>=beta: flag=TT_LOWER
        tt[key]=(depth,best_val,flag,best_move)
    return best_val

def search_root(board,depth,turn,ep,cr,tt,start_time,time_limit,progress_cb=None):
    moves=all_legal(board,turn,ep,cr)
    if not moves: return (0,None) if not in_check(board,turn) else (-(MATE-0),None)
    key=zobrist_hash(board,turn,ep,cr)
    entry=tt.get(key)
    tt_move=entry[3] if entry else None
    moves=order_moves(board,moves,tt_move)
    alpha,beta=-INF,INF
    best_val=-INF; best_move=moves[0]
    for i,(fr,fc,tr,tc) in enumerate(moves):
        p=board[fr][fc]
        nb=apply_move(board,fr,fc,tr,tc,ep,cr)
        new_ep=next_ep(board,fr,fc,tr,tc)
        new_cr=upd_cr(cr,p,fr,fc,board,tr,tc)
        val=-negamax(nb,depth-1,-beta,-alpha,opp(turn),new_ep,new_cr,tt,1,start_time,time_limit)
        if val>best_val: best_val=val; best_move=(fr,fc,tr,tc)
        if val>alpha: alpha=val
        if progress_cb:
            progress_cb({'phase':'searching','depth':depth,'candidate':(fr,fc,tr,tc),
                         'move_index':i+1,'move_count':len(moves),
                         'best_move':best_move,'best_eval':best_val,
                         'elapsed':time.time()-start_time})
    if len(tt)<2_000_000: tt[key]=(depth,best_val,TT_EXACT,best_move)
    return best_val,best_move

def iterative_deepening(board,turn,ep,cr,tt,time_limit=3.0,max_depth=8,progress_cb=None):
    start=time.time()
    best_move=None; best_val=0; depth=1
    while depth<=max_depth and time.time()-start<time_limit:
        try:
            val,move=search_root(board,depth,turn,ep,cr,tt,start,time_limit,progress_cb)
        except TimeUp:
            break
        if move is not None: best_move,best_val=move,val
        if progress_cb:
            progress_cb({'phase':'depth_done','depth':depth,'best_move':best_move,
                         'best_eval':best_val,'elapsed':time.time()-start})
        if abs(val)>=MATE_THRESHOLD: break
        depth+=1
    if progress_cb:
        progress_cb({'phase':'done','depth':depth-1,'best_move':best_move,
                     'best_eval':best_val,'elapsed':time.time()-start})
    return best_val,best_move

async def search_root_async(board,depth,turn,ep,cr,tt,start_time,time_limit,progress_cb=None):
    """Same as search_root(), but yields to the browser's event loop after each root move so a
       WASM build (no real OS threads) doesn't freeze the tab while the AI thinks."""
    moves=all_legal(board,turn,ep,cr)
    if not moves: return (0,None) if not in_check(board,turn) else (-(MATE-0),None)
    key=zobrist_hash(board,turn,ep,cr)
    entry=tt.get(key)
    tt_move=entry[3] if entry else None
    moves=order_moves(board,moves,tt_move)
    alpha,beta=-INF,INF
    best_val=-INF; best_move=moves[0]
    for i,(fr,fc,tr,tc) in enumerate(moves):
        p=board[fr][fc]
        nb=apply_move(board,fr,fc,tr,tc,ep,cr)
        new_ep=next_ep(board,fr,fc,tr,tc)
        new_cr=upd_cr(cr,p,fr,fc,board,tr,tc)
        val=-negamax(nb,depth-1,-beta,-alpha,opp(turn),new_ep,new_cr,tt,1,start_time,time_limit)
        if val>best_val: best_val=val; best_move=(fr,fc,tr,tc)
        if val>alpha: alpha=val
        if progress_cb:
            progress_cb({'phase':'searching','depth':depth,'candidate':(fr,fc,tr,tc),
                         'move_index':i+1,'move_count':len(moves),
                         'best_move':best_move,'best_eval':best_val,
                         'elapsed':time.time()-start_time})
        await asyncio.sleep(0)
    if len(tt)<2_000_000: tt[key]=(depth,best_val,TT_EXACT,best_move)
    return best_val,best_move

async def iterative_deepening_async(board,turn,ep,cr,tt,time_limit=3.0,max_depth=8,progress_cb=None):
    start=time.time()
    best_move=None; best_val=0; depth=1
    while depth<=max_depth and time.time()-start<time_limit:
        try:
            val,move=await search_root_async(board,depth,turn,ep,cr,tt,start,time_limit,progress_cb)
        except TimeUp:
            break
        if move is not None: best_move,best_val=move,val
        if progress_cb:
            progress_cb({'phase':'depth_done','depth':depth,'best_move':best_move,
                         'best_eval':best_val,'elapsed':time.time()-start})
        if abs(val)>=MATE_THRESHOLD: break
        depth+=1
        await asyncio.sleep(0)
    if progress_cb:
        progress_cb({'phase':'done','depth':depth-1,'best_move':best_move,
                     'best_eval':best_val,'elapsed':time.time()-start})
    return best_val,best_move

async def get_top_moves_async(board,turn,ep,cr,tt,depth=3,top_n=3,time_limit=2.0):
    """Async twin of get_top_moves(), yielding after each root move for the web build."""
    moves=all_legal(board,turn,ep,cr)
    if not moves: return []
    start=time.time()
    scored=[]
    for fr,fc,tr,tc in moves:
        p=board[fr][fc]
        nb=apply_move(board,fr,fc,tr,tc,ep,cr)
        new_ep=next_ep(board,fr,fc,tr,tc)
        new_cr=upd_cr(cr,p,fr,fc,board,tr,tc)
        try:
            val=-negamax(nb,depth-1,-INF,INF,opp(turn),new_ep,new_cr,tt,1,start,time_limit)
        except TimeUp:
            val=evaluate(nb) if turn=='w' else -evaluate(nb)
        san=to_san(board,fr,fc,tr,tc,ep,cr,'Q',nb,opp(turn),new_ep,new_cr)
        scored.append(((fr,fc,tr,tc),val,san))
        await asyncio.sleep(0)
    scored.sort(key=lambda x:x[1],reverse=True)
    return scored[:top_n]

def get_top_moves(board,turn,ep,cr,tt,depth=3,top_n=3,time_limit=2.0):
    """Multi-PV-style shallow search: evaluate every legal root move, return the best `top_n`
       as (move, eval_relative_to_turn, san) sorted best-first."""
    moves=all_legal(board,turn,ep,cr)
    if not moves: return []
    start=time.time()
    scored=[]
    for fr,fc,tr,tc in moves:
        p=board[fr][fc]
        nb=apply_move(board,fr,fc,tr,tc,ep,cr)
        new_ep=next_ep(board,fr,fc,tr,tc)
        new_cr=upd_cr(cr,p,fr,fc,board,tr,tc)
        try:
            val=-negamax(nb,depth-1,-INF,INF,opp(turn),new_ep,new_cr,tt,1,start,time_limit)
        except TimeUp:
            val=evaluate(nb) if turn=='w' else -evaluate(nb)
        san=to_san(board,fr,fc,tr,tc,ep,cr,'Q',nb,opp(turn),new_ep,new_cr)
        scored.append(((fr,fc,tr,tc),val,san))
    scored.sort(key=lambda x:x[1],reverse=True)
    return scored[:top_n]

# ═══════════════════════════════════════════════════════════════════════════════
#  STOCKFISH (optional external backend)
# ═══════════════════════════════════════════════════════════════════════════════
class StockfishEngine:
    """Thin UCI wrapper around a local `stockfish` binary. Any failure at any stage
       leaves the engine unusable (self.ok=False) so callers can fall back to the
       internal engine without crashing."""
    _INFO_RE=re.compile(r'depth (\d+).*?currmove (\S+)|depth (\d+).*?score (cp|mate) (-?\d+)')

    def __init__(self,path='stockfish'):
        self.ok=False
        self.proc=None
        try:
            self.proc=subprocess.Popen([path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL,text=True,bufsize=1)
            self._send('uci'); self._read_until('uciok',3.0)
            self._send('isready'); self._read_until('readyok',3.0)
            self.ok=True
        except Exception:
            self.ok=False

    def _send(self,cmd):
        self.proc.stdin.write(cmd+'\n'); self.proc.stdin.flush()

    def _read_until(self,token,timeout):
        start=time.time(); lines=[]
        while time.time()-start<timeout:
            line=self.proc.stdout.readline()
            if not line: break
            lines.append(line.strip())
            if token in line: break
        return lines

    def best_move(self,fen,movetime_ms=1500,progress_cb=None):
        if not self.ok: return None
        try:
            self._send('ucinewgame')
            self._send(f'position fen {fen}')
            self._send(f'go movetime {movetime_ms}')
            start=time.time(); timeout=movetime_ms/1000.0+2.0
            while time.time()-start<timeout:
                line=self.proc.stdout.readline()
                if not line: break
                line=line.strip()
                if progress_cb and line.startswith('info'):
                    progress_cb(self._parse_info(line,start))
                if line.startswith('bestmove'):
                    parts=line.split()
                    mv=parts[1] if len(parts)>1 else None
                    return None if mv in (None,'(none)') else mv
        except Exception:
            self.ok=False
        return None

    def _parse_info(self,line,start_time):
        info={'phase':'searching','elapsed':time.time()-start_time,'engine':'stockfish'}
        dm=re.search(r'\bdepth (\d+)',line)
        if dm: info['depth']=int(dm.group(1))
        cm=re.search(r'\bcurrmove (\S+)',line)
        if cm: info['candidate_uci']=cm.group(1)
        sm=re.search(r'\bscore (cp|mate) (-?\d+)',line)
        if sm: info['score_type']=sm.group(1); info['score_val']=int(sm.group(2))
        return info

    def close(self):
        if not self.proc: return
        try:
            self._send('quit')
            self.proc.wait(timeout=1.0)
        except Exception:
            try: self.proc.terminate()
            except Exception: pass

# ═══════════════════════════════════════════════════════════════════════════════
#  PUZZLES
# ═══════════════════════════════════════════════════════════════════════════════
PUZZLES_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'puzzles.json')
DEFAULT_PUZZLES=[
    {"fen":"6k1/5ppp/8/8/8/8/8/R6K w - - 0 1","solution":["a1a8"],
     "description":"Mat en 1 — la tour livre le mat sur la 8e rangée"},
    {"fen":"r6k/8/8/8/8/8/5PPP/6K1 b - - 0 1","solution":["a8a1"],
     "description":"Mat en 1 — la tour noire livre le mat sur la 1re rangée"},
    {"fen":"6rk/6pp/7N/8/8/8/8/K7 w - - 0 1","solution":["h6f7"],
     "description":"Mat étouffé en 1 — le cavalier livre le mat"},
]

def load_puzzles():
    if os.path.exists(PUZZLES_FILE):
        try:
            with open(PUZZLES_FILE,'r',encoding='utf-8') as f:
                data=json.load(f)
            if isinstance(data,list) and data: return data
        except Exception:
            pass
    try:
        with open(PUZZLES_FILE,'w',encoding='utf-8') as f:
            json.dump(DEFAULT_PUZZLES,f,ensure_ascii=False,indent=2)
    except Exception:
        pass
    return DEFAULT_PUZZLES

# ═══════════════════════════════════════════════════════════════════════════════
#  GAME STATE
# ═══════════════════════════════════════════════════════════════════════════════
CLOCK_PRESETS=[("1 min",60),("3 min",180),("5 min",300),("10 min",600)]

class Game:
    def __init__(self):
        self.theme_idx=0
        self.piece_style_idx=0
        self.ai_depth=4
        self.use_stockfish=False
        self.stockfish=None
        if shutil.which('stockfish'):
            try:
                eng=StockfishEngine()
                if eng.ok: self.stockfish=eng
            except Exception:
                self.stockfish=None
        self.analysis_mode=False
        self.blind_mode=False
        self.chrono_enabled=False
        self.clock_initial=180
        self.puzzles=load_puzzles()
        self.puzzle_index=0
        self.reset()

    # ---- lifecycle ----
    def reset(self):
        self.board=start_board()
        self.turn='w'
        self.ep=None
        self.cr=deepcopy({'w':{'K':True,'Q':True},'b':{'K':True,'Q':True}})
        self.halfmove_clock=0
        self.fullmove_number=1
        self.selected=None
        self.legal=[]
        self.status='playing'
        self.san_history=[]        # SAN strings, ply order
        self.eval_history=[0.0]    # White-relative eval (pawns) after each ply, index0 = start
        self.position_snapshots=[self._snapshot_position()]
        self.position_counts={}
        self._register_position()
        self.undo_stack=[]
        self.promotion_pending=None
        self.flip=False
        self.mode='pvp'        # 'pvp' | 'vs_ai' | 'puzzle'
        self.ai_color='b'
        self.ai_thinking=False
        self.ai_result=None
        self.ai_progress={}
        self.hint_computing=False
        self.top_moves=[]           # [(move,white_relative_eval,san), ...]
        self.top_moves_source=None  # 'hint' | 'analysis' — which feature last populated top_moves
        self.analysis_suggestion=None  # single best move (fr,fc,tr,tc) shown as green arrow
        self.tt={}
        self.puzzle_mode=False
        self.puzzle_status=None
        self.puzzle_solution=[]
        self.replay_index=None      # None == live; else index into position_snapshots
        self.clock_w=float(self.clock_initial)
        self.clock_b=float(self.clock_initial)
        self.status_message=''
        self.status_message_until=0
        self.fen_input_active=False
        self.fen_input_text=''
        self.last_move=None
        self.last_move_is_capture=False
        self.edit_mode=False        # sandbox mode: free piece placement/movement
        self.edit_piece=None        # piece code ('wK'...) selected in the palette, 'erase', or None (free-move tool)
        self.edit_selected=None     # (r,c) picked up with the free-move tool, awaiting a destination

    def theme(self): return THEMES[THEME_NAMES[self.theme_idx]]
    def piece_style(self): return PIECE_STYLES[self.piece_style_idx]
    def col_name(self,col): return 'Blancs' if col=='w' else 'Noirs'

    def flash(self,msg,seconds=2.5):
        self.status_message=msg; self.status_message_until=time.time()+seconds

    def _snapshot_position(self):
        return {'board':[r[:] for r in self.board],'turn':self.turn,'ep':self.ep,
                'cr':deepcopy(self.cr),'status':self.status}

    def _register_position(self):
        key=zobrist_hash(self.board,self.turn,self.ep,self.cr)
        self.position_counts[key]=self.position_counts.get(key,0)+1
        return self.position_counts[key]

    # ---- undo/redo bookkeeping ----
    def save_snapshot(self):
        self.undo_stack.append({
            'board':[r[:] for r in self.board],
            'turn':self.turn,'ep':self.ep,'cr':deepcopy(self.cr),
            'status':self.status,'san_history':self.san_history[:],
            'eval_history':self.eval_history[:],
            'position_snapshots':self.position_snapshots[:],
            'position_counts':dict(self.position_counts),
            'halfmove_clock':self.halfmove_clock,'fullmove_number':self.fullmove_number,
        })

    def undo(self):
        if not self.undo_stack or self.puzzle_mode: return
        if self.mode=='vs_ai' and len(self.undo_stack)>=2:
            self.undo_stack.pop()
        s=self.undo_stack.pop()
        self.board=s['board']; self.turn=s['turn']; self.ep=s['ep']; self.cr=s['cr']
        self.status=s['status']; self.san_history=s['san_history']
        self.eval_history=s['eval_history']; self.position_snapshots=s['position_snapshots']
        self.position_counts=s['position_counts']
        self.halfmove_clock=s['halfmove_clock']; self.fullmove_number=s['fullmove_number']
        self.top_moves=[]; self.analysis_suggestion=None
        self.selected=None; self.legal=[]
        self.ai_result=None; self.ai_thinking=False
        self.replay_index=None; self.last_move=None

    # ---- core move application (shared by human clicks, AI, puzzles) ----
    def do_move(self,fr,fc,tr,tc,promote='Q'):
        self.save_snapshot()
        piece=self.board[fr][fc]
        capture=is_capture_move(self.board,fr,fc,tr,tc,self.ep)
        pawn_move=kind_of(piece)=='P'
        new_ep=next_ep(self.board,fr,fc,tr,tc)
        new_cr=upd_cr(self.cr,piece,fr,fc,self.board,tr,tc)
        new_board=apply_move(self.board,fr,fc,tr,tc,self.ep,self.cr,promote)
        post_turn=opp(self.turn)
        san=to_san(self.board,fr,fc,tr,tc,self.ep,self.cr,promote,new_board,post_turn,new_ep,new_cr)

        self.board=new_board; self.ep=new_ep; self.cr=new_cr
        self.halfmove_clock = 0 if (capture or pawn_move) else self.halfmove_clock+1
        if self.turn=='b': self.fullmove_number+=1
        self.last_move=(fr,fc,tr,tc); self.last_move_is_capture=capture
        self.turn=post_turn
        self.san_history.append(san)
        if len(self.san_history)>1000: self.san_history=self.san_history[-1000:]
        self.selected=None; self.legal=[]
        self.top_moves=[]; self.analysis_suggestion=None
        self.replay_index=None

        self._update_status()
        white_eval=evaluate(self.board)/100.0
        self.eval_history.append(white_eval)
        self.position_snapshots.append(self._snapshot_position())
        rep_count=self._register_position()
        if self.status in ('playing','check'):
            if rep_count>=3: self.status='draw_repetition'
            elif self.halfmove_clock>=100: self.status='draw_50move'

    def _update_status(self):
        ic=in_check(self.board,self.turn)
        hm=bool(all_legal(self.board,self.turn,self.ep,self.cr))
        if not hm: self.status='checkmate' if ic else 'stalemate'
        elif ic:   self.status='check'
        else:      self.status='playing'

    def is_over(self):
        return self.status not in ('playing','check')

    def pgn_result(self):
        if self.status=='checkmate': return '1-0' if opp(self.turn)=='w' else '0-1'
        if self.status=='timeout_w': return '0-1'
        if self.status=='timeout_b': return '1-0'
        if self.status in ('stalemate','draw_repetition','draw_50move'): return '1/2-1/2'
        return '*'

    # ---- interaction ----
    def is_live(self): return self.replay_index is None

    def display_state(self):
        """Board/turn/status to RENDER (may be a replay snapshot, never mutates real state)."""
        if self.replay_index is None or self.replay_index>=len(self.position_snapshots)-1:
            return self.board,self.turn,self.status
        snap=self.position_snapshots[self.replay_index]
        return snap['board'],snap['turn'],snap['status']

    def enter_replay(self,index):
        index=max(0,min(index,len(self.position_snapshots)-1))
        self.replay_index=None if index==len(self.position_snapshots)-1 else index

    def replay_step(self,delta):
        cur=self.replay_index if self.replay_index is not None else len(self.position_snapshots)-1
        self.enter_replay(cur+delta)

    def click(self,r,c):
        if self.fen_input_active: return
        if not self.is_live(): return
        if self.status in ('checkmate','stalemate','draw_repetition','draw_50move','timeout_w','timeout_b'): return
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
                    self._commit_move(fr,fc,r,c)
                return
            self.selected=None; self.legal=[]
        if p and col_of(p)==self.turn:
            self.selected=(r,c)
            self.legal=legal_moves(self.board,r,c,self.ep,self.cr)

    def promote(self,kind):
        if not self.promotion_pending: return
        fr,fc,tr,tc=self.promotion_pending
        self.promotion_pending=None
        self._commit_move(fr,fc,tr,tc,promote=kind)

    def _commit_move(self,fr,fc,tr,tc,promote='Q'):
        """Routes a completed human move through puzzle-checking or straight into do_move."""
        if self.puzzle_mode:
            self._puzzle_attempt(fr,fc,tr,tc,promote)
        else:
            self.do_move(fr,fc,tr,tc,promote)
            if self.analysis_mode and self.status in ('playing','check'):
                self.start_analysis()

    # ---- edit mode (sandbox: free placement/movement of pieces) ----
    def toggle_edit_mode(self):
        if self.edit_mode:
            self.edit_mode=False
            self.edit_piece=None; self.edit_selected=None
            self._finish_edit()
        else:
            self.edit_mode=True
            self.edit_piece=None; self.edit_selected=None
            self.selected=None; self.legal=[]
            self.promotion_pending=None
            if self.puzzle_mode:
                self.puzzle_mode=False; self.mode='pvp'

    def edit_click(self,r,c):
        if not self.edit_mode: return
        if self.edit_piece=='erase':
            self.board[r][c]=None
        elif self.edit_piece:
            if kind_of(self.edit_piece)=='K':
                # only one king per color: placing one relocates it instead of duplicating
                col=col_of(self.edit_piece)
                for rr in range(8):
                    for cc in range(8):
                        if self.board[rr][cc]==self.edit_piece: self.board[rr][cc]=None
            self.board[r][c]=self.edit_piece
        else:
            if self.edit_selected:
                fr,fc=self.edit_selected
                if (fr,fc)!=(r,c):
                    self.board[r][c]=self.board[fr][fc]
                    self.board[fr][fc]=None
                self.edit_selected=None
            elif self.board[r][c]:
                self.edit_selected=(r,c)

    def edit_clear_board(self):
        self.board=[[None]*8 for _ in range(8)]
        self.edit_selected=None

    def edit_reset_start(self):
        self.board=start_board()
        self.edit_selected=None

    def _finish_edit(self):
        """Treat the edited board like a freshly loaded position: rights reset to permissive
           defaults, history cleared (past moves no longer describe this board)."""
        self.cr={'w':{'K':True,'Q':True},'b':{'K':True,'Q':True}}
        self.ep=None
        self.halfmove_clock=0; self.fullmove_number=1
        self.san_history=[]
        self.eval_history=[evaluate(self.board)/100.0]
        self.position_snapshots=[self._snapshot_position()]
        self.position_counts={}
        self._register_position()
        self.undo_stack=[]
        self.selected=None; self.legal=[]
        self.top_moves=[]; self.analysis_suggestion=None
        self.replay_index=None; self.tt={}
        self.last_move=None
        self._update_status()

    # ---- AI ----
    def start_ai_move(self):
        if self.ai_thinking: return
        self.ai_thinking=True
        self.ai_progress={}
        board,turn,ep,cr=self.board,self.ai_color,self.ep,self.cr
        if IS_WEB:
            async def run_async():
                val,mv=await iterative_deepening_async(board,turn,ep,cr,self.tt,3.0,self.ai_depth,
                                                         lambda info:setattr(self,'ai_progress',info))
                self.ai_result=(mv[0],mv[1],mv[2],mv[3],'Q') if mv else None
            asyncio.ensure_future(run_async())
            return
        def run():
            if self.stockfish and self.use_stockfish:
                fen=board_to_fen(board,turn,cr,ep,self.halfmove_clock,self.fullmove_number)
                def cb(info): self.ai_progress=info
                uci=self.stockfish.best_move(fen,movetime_ms=1500,progress_cb=cb)
                move=None
                if uci:
                    try:
                        f_r,f_c,t_r,t_c,promo=parse_uci_move(uci)
                        move=(f_r,f_c,t_r,t_c,promo)
                    except Exception:
                        move=None
                if move is None:
                    val,mv=iterative_deepening(board,turn,ep,cr,self.tt,3.0,self.ai_depth,
                                                lambda info:setattr(self,'ai_progress',info))
                    move=(mv[0],mv[1],mv[2],mv[3],'Q') if mv else None
            else:
                val,mv=iterative_deepening(board,turn,ep,cr,self.tt,3.0,self.ai_depth,
                                            lambda info:setattr(self,'ai_progress',info))
                move=(mv[0],mv[1],mv[2],mv[3],'Q') if mv else None
            self.ai_result=move
        threading.Thread(target=run,daemon=True).start()

    def apply_ai_result(self):
        move=self.ai_result; self.ai_result=None; self.ai_thinking=False
        if move:
            fr,fc,tr,tc,promote=move
            self.do_move(fr,fc,tr,tc,promote)
            if self.analysis_mode and self.status in ('playing','check'):
                self.start_analysis()

    # ---- hints / analysis / top moves (shared computation) ----
    @staticmethod
    def _to_white_relative(top,turn):
        """get_top_moves() returns evals relative to the side that moved; normalize to
           White-positive pawns so rendering never needs to know whose turn it was."""
        sign=1.0 if turn=='w' else -1.0
        return [(mv,sign*val/100.0,san) for mv,val,san in top]

    def start_hint(self):
        if self.hint_computing or not self.is_live(): return
        self.hint_computing=True
        self.analysis_suggestion=None
        board,turn,ep,cr,tt=self.board,self.turn,self.ep,self.cr,self.tt
        if IS_WEB:
            async def run_async():
                top=await get_top_moves_async(board,turn,ep,cr,tt,depth=3,top_n=3,time_limit=2.0)
                self.top_moves=self._to_white_relative(top,turn)
                self.top_moves_source='hint'
                self.hint_computing=False
            asyncio.ensure_future(run_async())
            return
        def run():
            top=get_top_moves(board,turn,ep,cr,tt,depth=3,top_n=3,time_limit=2.0)
            self.top_moves=self._to_white_relative(top,turn)
            self.top_moves_source='hint'
            self.hint_computing=False
        threading.Thread(target=run,daemon=True).start()

    def start_analysis(self):
        """Suggests the best reply for whichever side is now to move (used after a human move
           in Analysis mode); drawn as a fixed green arrow, independent of the hint panel."""
        if self.hint_computing: return
        self.hint_computing=True
        board,turn,ep,cr,tt=self.board,self.turn,self.ep,self.cr,self.tt
        if IS_WEB:
            async def run_async():
                top=await get_top_moves_async(board,turn,ep,cr,tt,depth=3,top_n=3,time_limit=2.0)
                self.top_moves=self._to_white_relative(top,turn)
                self.top_moves_source='analysis'
                self.analysis_suggestion=top[0][0] if top else None
                self.hint_computing=False
            asyncio.ensure_future(run_async())
            return
        def run():
            top=get_top_moves(board,turn,ep,cr,tt,depth=3,top_n=3,time_limit=2.0)
            self.top_moves=self._to_white_relative(top,turn)
            self.top_moves_source='analysis'
            self.analysis_suggestion=top[0][0] if top else None
            self.hint_computing=False
        threading.Thread(target=run,daemon=True).start()

    # ---- puzzles ----
    def load_puzzle(self,index):
        if not self.puzzles: return
        index=index % len(self.puzzles)
        self.puzzle_index=index
        puzzle=self.puzzles[index]
        try:
            board,turn,cr,ep,halfmove,fullmove=board_from_fen(puzzle['fen'])
        except Exception as ex:
            self.flash(f"FEN de puzzle invalide : {ex}"); return
        self.board=board; self.turn=turn; self.cr=cr; self.ep=ep
        self.halfmove_clock=halfmove; self.fullmove_number=fullmove
        self.san_history=[]; self.eval_history=[evaluate(board)/100.0]
        self.position_snapshots=[self._snapshot_position()]
        self.position_counts={}; self._register_position()
        self.undo_stack=[]; self.selected=None; self.legal=[]
        self.top_moves=[]; self.analysis_suggestion=None
        self.replay_index=None; self.tt={}; self.last_move=None
        self.mode='puzzle'; self.puzzle_mode=True
        self.puzzle_solution=list(puzzle.get('solution',[]))
        self.puzzle_status=None
        self._update_status()

    def exit_puzzle(self):
        self.puzzle_mode=False; self.mode='pvp'; self.puzzle_status=None
        self.reset()

    def _puzzle_attempt(self,fr,fc,tr,tc,promote):
        if not self.puzzle_solution:
            return
        is_promo = kind_of(self.board[fr][fc])=='P' and (tr==0 or tr==7)
        attempted=to_uci_move(fr,fc,tr,tc,promote,is_promo)
        expected=self.puzzle_solution[0]
        # accept either 4-char or promotion-suffixed expected notation
        matches = attempted==expected or attempted[:4]==expected[:4]
        if not matches:
            self.puzzle_status='wrong'
            self.selected=None; self.legal=[]
            self.flash("Incorrect — réessayez",1.6)
            return
        self.do_move(fr,fc,tr,tc,promote)
        self.puzzle_solution.pop(0)
        if self.puzzle_solution:
            reply=self.puzzle_solution.pop(0)
            try:
                rf,rc,rt,rc2,rp=parse_uci_move(reply)
                self.do_move(rf,rc,rt,rc2,rp)
            except Exception:
                pass
        if self.puzzle_solution:
            self.puzzle_status='correct'
            self.flash("Bien joué ! Continuez…",1.6)
        else:
            self.puzzle_status='solved'
            self.flash("Puzzle résolu ! 🎉",3.0)

    # ---- PGN / FEN plumbing ----
    def current_fen(self):
        return board_to_fen(self.board,self.turn,self.cr,self.ep,self.halfmove_clock,self.fullmove_number)

    def load_fen(self,fen):
        board,turn,cr,ep,halfmove,fullmove=board_from_fen(fen)
        self.board=board; self.turn=turn; self.cr=cr; self.ep=ep
        self.halfmove_clock=halfmove; self.fullmove_number=fullmove
        self.san_history=[]; self.eval_history=[evaluate(board)/100.0]
        self.position_snapshots=[self._snapshot_position()]
        self.position_counts={}; self._register_position()
        self.undo_stack=[]; self.selected=None; self.legal=[]
        self.top_moves=[]; self.analysis_suggestion=None; self.replay_index=None
        self.tt={}; self.puzzle_mode=False; self.last_move=None
        self._update_status()

    def export_pgn(self,filepath=None):
        if filepath is None:
            filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   f"partie_{time.strftime('%Y%m%d_%H%M%S')}.pgn")
        headers=[
            ('Event','Partie locale'), ('Site','Chess Pro (Python/pygame)'),
            ('Date',time.strftime('%Y.%m.%d')), ('Round','1'),
            ('White','Joueur' if self.mode!='vs_ai' or self.ai_color=='b' else 'IA'),
            ('Black','IA' if self.mode=='vs_ai' and self.ai_color=='b' else 'Joueur'),
            ('Result',self.pgn_result()),
        ]
        lines=[f'[{k} "{v}"]' for k,v in headers]
        movetext=[]
        for i,san in enumerate(self.san_history):
            if i%2==0: movetext.append(f"{i//2+1}.")
            movetext.append(san)
        movetext.append(self.pgn_result())
        wrapped=textwrap.wrap(' '.join(movetext),width=78)
        with open(filepath,'w',encoding='utf-8') as f:
            f.write('\n'.join(lines)+'\n\n')
            f.write('\n'.join(wrapped)+'\n')
        self.flash(f"PGN exporté : {os.path.basename(filepath)}",3.0)
        return filepath

    def save_fen_to_file(self):
        filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),'positions.fen')
        with open(filepath,'a',encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {self.current_fen()}\n")
        self.flash(f"Position sauvée dans {os.path.basename(filepath)}",2.5)

    # ---- chrono ----
    def tick_clock(self,dt):
        if not self.chrono_enabled or self.is_over() or self.puzzle_mode or not self.is_live() or self.edit_mode:
            return
        if self.turn=='w':
            self.clock_w=max(0.0,self.clock_w-dt)
            if self.clock_w<=0: self.status='timeout_w'
        else:
            self.clock_b=max(0.0,self.clock_b-dt)
            if self.clock_b<=0: self.status='timeout_b'

    def set_clock_preset(self,seconds):
        self.clock_initial=seconds
        self.clock_w=float(seconds); self.clock_b=float(seconds)

# ═══════════════════════════════════════════════════════════════════════════════
#  RENDERING
# ═══════════════════════════════════════════════════════════════════════════════
BOARD_SIZE=720; GRAPH_H=90; PANEL_W=340; EVAL_BAR_W=34
BOARD_X=EVAL_BAR_W                 # board is offset right of the eval bar, chess.com-style
PANEL_X=BOARD_X+BOARD_SIZE
H=BOARD_SIZE+GRAPH_H; W=BOARD_X+BOARD_SIZE+PANEL_W; SQ=BOARD_SIZE//8
PANEL_SURF_H=3200   # generous fixed virtual height; the panel scrolls within the H-tall window

class Renderer:
    def __init__(self,screen):
        self.screen=screen
        self._init_fonts()
        self.board_surf=pygame.Surface((BOARD_SIZE,BOARD_SIZE))
        self.graph_surf=pygame.Surface((BOARD_SIZE,GRAPH_H))
        self.eval_bar_surf=pygame.Surface((EVAL_BAR_W,BOARD_SIZE))
        self.panel=pygame.Surface((PANEL_W,PANEL_SURF_H))
        self._anim_t=0
        self.scroll_y=0
        self._panel_content_h=H
        self._x0=14
        self._last_seen_move=None
        self._blind_reveal_sq=None
        self._blind_reveal_until=0
        self._eval_bar_value=0.0        # currently displayed (animated) value
        self._eval_bar_anim_from=0.0
        self._eval_bar_anim_to=0.0
        self._eval_bar_anim_start=0.0
        self._eval_bar_anim_dur=0.45
        self._eval_bar_last_raw=None    # last real eval seen, to detect an actual change

    def _init_fonts(self):
        # pygame.font.SysFont() never raises and never returns None for an unmatched name — it
        # silently substitutes its own default font — so a try/except fallback loop around it can
        # never actually detect a miss. match_font() is the only reliable way to check a family is
        # really installed (and, critically, whether it covers the chess glyph block U+2654-265F).
        def load(names,size,bold=False):
            for n in names:
                path=pygame.font.match_font(n,bold=bold)
                if path:
                    try: return pygame.font.Font(path,size)
                    except Exception: continue
            return pygame.font.Font(None,size)
        text_names=['DejaVu Sans','Noto Sans','Segoe UI','Helvetica','Arial','sans-serif']
        sym_names=['FreeSerif','DejaVu Sans','Noto Sans Symbols2','Segoe UI Symbol','Symbola']
        self.fL=load(text_names,26,True); self.fM=load(text_names,17,True); self.fS=load(text_names,13)
        self.fXS=load(text_names,11)
        self.fSym=load(sym_names,SQ-6); self.fSymB=load(sym_names,SQ); self.fSymS=load(sym_names,SQ-18)

    def sq_to_px(self,r,c,flip):
        dr=7-r if flip else r; dc=7-c if flip else c
        return dc*SQ,dr*SQ

    def _move_label(self,mv):
        if not mv: return ''
        fr,fc,tr,tc=mv[:4]
        return f"{sq_name(fr,fc)}-{sq_name(tr,tc)}"

    def _update_blind_reveal(self,game):
        if not (game.blind_mode and game.mode=='vs_ai'): return
        if game.last_move==self._last_seen_move: return
        self._last_seen_move=game.last_move
        if game.last_move and game.last_move_is_capture:
            fr,fc,tr,tc=game.last_move
            mover=game.board[tr][tc]
            if mover and col_of(mover)==game.ai_color:
                self._blind_reveal_sq=(tr,tc)
                self._blind_reveal_until=time.time()+2.5

    def draw(self,game,dt):
        self._anim_t+=dt
        T=game.theme()
        self.screen.fill(T['panel_bg'])
        self._update_blind_reveal(game)
        self._draw_board(game,T)
        self._draw_graph(game,T)
        self._draw_panel(game,T)
        self._draw_toast(game,T)
        if game.promotion_pending:
            self._draw_promotion(game,T)
        if game.fen_input_active:
            self._draw_fen_modal(game,T)

    def _draw_board(self,game,T):
        flip=game.flip
        board,turn_disp,status_disp=game.display_state()
        live=game.is_live()

        for r in range(8):
            for c in range(8):
                x,y=self.sq_to_px(r,c,flip)
                col=T['light'] if (r+c)%2==0 else T['dark']
                pygame.draw.rect(self.board_surf,col,(x,y,SQ,SQ))

        if game.last_move:
            for (rr,cc) in (game.last_move[0:2],game.last_move[2:4]):
                x,y=self.sq_to_px(rr,cc,flip)
                ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA); ov.fill((255,255,255,35))
                self.board_surf.blit(ov,(x,y))

        if game.analysis_suggestion and live:
            fr,fc,tr,tc=game.analysis_suggestion
            x1,y1=self.sq_to_px(fr,fc,flip); x1+=SQ//2; y1+=SQ//2
            x2,y2=self.sq_to_px(tr,tc,flip); x2+=SQ//2; y2+=SQ//2
            self._draw_arrow(x1,y1,x2,y2,ANALYSIS_GREEN)

        if game.top_moves and game.top_moves_source=='hint' and live:
            for i,(mv,ev,san) in enumerate(game.top_moves):
                fr,fc,tr,tc=mv
                x1,y1=self.sq_to_px(fr,fc,flip); x1+=SQ//2; y1+=SQ//2
                x2,y2=self.sq_to_px(tr,tc,flip); x2+=SQ//2; y2+=SQ//2
                hcol=T['hint_best'] if i==0 else T['hint_good']
                self._draw_arrow(x1,y1,x2,y2,hcol)

        if live and game.selected:
            sr,sc=game.selected; x,y=self.sq_to_px(sr,sc,flip)
            ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA); ov.fill(T['hl']); self.board_surf.blit(ov,(x,y))
        if game.edit_mode and game.edit_selected:
            sr,sc=game.edit_selected; x,y=self.sq_to_px(sr,sc,flip)
            ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA); ov.fill(T['hl']); self.board_surf.blit(ov,(x,y))
        if live:
            for tr,tc in game.legal:
                x,y=self.sq_to_px(tr,tc,flip)
                ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
                if board[tr][tc]:
                    pygame.draw.rect(ov,T['legal'],(0,0,SQ,SQ),5)
                else:
                    pygame.draw.circle(ov,T['legal'],(SQ//2,SQ//2),SQ//7)
                self.board_surf.blit(ov,(x,y))

        if status_disp in ('check','checkmate'):
            kp=king_pos(board,turn_disp)
            if kp:
                x,y=self.sq_to_px(kp[0],kp[1],flip)
                ov=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
                alpha=int(120+80*abs(math.sin(self._anim_t*3)))
                ov.fill((*T['check'][:3],alpha))
                self.board_surf.blit(ov,(x,y))

        for i in range(8):
            lf=self.fXS.render(FILES[i] if not flip else FILES[7-i],False,T['coord'])
            self.board_surf.blit(lf,(i*SQ+SQ-13,BOARD_SIZE-13))
            lr=self.fXS.render(RANKS[i] if not flip else RANKS[7-i],False,T['coord'])
            self.board_surf.blit(lr,(3,i*SQ+3))

        hide_color=game.ai_color if (game.blind_mode and game.mode=='vs_ai') else None
        reveal_sq=self._blind_reveal_sq if time.time()<self._blind_reveal_until else None
        for r in range(8):
            for c in range(8):
                p=board[r][c]
                if not p: continue
                if hide_color and col_of(p)==hide_color and (r,c)!=reveal_sq: continue
                x,y=self.sq_to_px(r,c,flip)
                self._draw_piece(p,x,y,game.piece_style(),T)

        self.screen.blit(self.board_surf,(BOARD_X,0))
        pygame.draw.rect(self.screen,T['accent'],(BOARD_X,0,BOARD_SIZE,BOARD_SIZE),2)

        self._draw_eval_bar(game,T)
        if game.puzzle_mode:
            self._draw_puzzle_banner(game,T)

    def _draw_eval_bar(self,game,T):
        """Vertical White/Black advantage gauge next to the board, chess.com-style: a logistic
           (win-probability-shaped) mapping so small edges are still visible and big ones saturate,
           and flips sides with the board. The displayed value only animates when the real
           evaluation actually changes (a move was made, or replay navigated to a different ply)
           — a bounded, eased transition that locks onto the exact target and stops, rather than a
           per-frame exponential chase that never fully settles and reads as random jitter."""
        idx=game.replay_index if game.replay_index is not None else len(game.eval_history)-1
        idx=max(0,min(idx,len(game.eval_history)-1))
        raw_eval=game.eval_history[idx]

        if self._eval_bar_last_raw is None:
            self._eval_bar_value=raw_eval
            self._eval_bar_anim_from=self._eval_bar_anim_to=raw_eval
            self._eval_bar_anim_start=self._anim_t
            self._eval_bar_last_raw=raw_eval
        elif raw_eval!=self._eval_bar_last_raw:
            self._eval_bar_anim_from=self._eval_bar_value
            self._eval_bar_anim_to=raw_eval
            self._eval_bar_anim_start=self._anim_t
            self._eval_bar_last_raw=raw_eval

        t=(self._anim_t-self._eval_bar_anim_start)/self._eval_bar_anim_dur
        t=max(0.0,min(1.0,t))
        eased=1-(1-t)**3
        self._eval_bar_value=self._eval_bar_anim_from+(self._eval_bar_anim_to-self._eval_bar_anim_from)*eased
        eval_now=self._eval_bar_value

        frac_white=1.0/(1.0+10**(-eval_now/4.0))
        white_px=int(round(BOARD_SIZE*frac_white))
        black_px=BOARD_SIZE-white_px
        flip=game.flip

        surf=self.eval_bar_surf
        surf.fill(T['piece_b'])
        white_y=0 if flip else black_px
        pygame.draw.rect(surf,T['piece_w'],(0,white_y,EVAL_BAR_W,white_px))
        boundary_y=white_px if flip else black_px

        label=f"{eval_now:+.1f}"
        if white_px<=black_px:
            lbl=self.fXS.render(label,False,T['piece_b'])
            ly=(boundary_y-lbl.get_height()-2) if flip else (boundary_y+2)
            ly=max(white_y+2,min(white_y+white_px-lbl.get_height()-2,ly))
        else:
            lbl=self.fXS.render(label,False,T['piece_w'])
            black_y=white_px if flip else 0
            ly=(boundary_y+2) if flip else (boundary_y-lbl.get_height()-2)
            ly=max(black_y+2,min(black_y+black_px-lbl.get_height()-2,ly))
        surf.blit(lbl,(EVAL_BAR_W//2-lbl.get_width()//2,ly))

        self.screen.blit(surf,(0,0))
        pygame.draw.rect(self.screen,T['accent'],(0,0,EVAL_BAR_W,BOARD_SIZE),1)

    def _draw_arrow(self,x1,y1,x2,y2,color,surf=None):
        target=surf if surf is not None else self.board_surf
        rgb=color[:3]; a=color[3] if len(color)>3 else 200
        layer=pygame.Surface((BOARD_SIZE,BOARD_SIZE),pygame.SRCALPHA)
        lw=6
        pygame.draw.line(layer,(*rgb,a),(x1,y1),(x2,y2),lw)
        ang=math.atan2(y2-y1,x2-x1)
        al=18; aa=0.5
        ax1=x2-al*math.cos(ang-aa); ay1=y2-al*math.sin(ang-aa)
        ax2=x2-al*math.cos(ang+aa); ay2=y2-al*math.sin(ang+aa)
        pygame.draw.polygon(layer,(*rgb,a),[(x2,y2),(ax1,ay1),(ax2,ay2)])
        target.blit(layer,(0,0))

    def _draw_piece(self,p,x,y,style,T):
        col=col_of(p); kind=kind_of(p)
        wc=T['piece_w'] if col=='w' else T['piece_b']
        oc=T['piece_w_out'] if col=='w' else T['piece_b_out']
        if style=='Symboles':
            sym=PIECE_CHARS_FILLED[p]
            sh=self.fSym.render(sym,False,(0,0,0))
            self.board_surf.blit(sh,(x+SQ//2-sh.get_width()//2+2,y+SQ//2-sh.get_height()//2+2))
            for dx,dy in[(-1,0),(1,0),(0,-1),(0,1)]:
                ol=self.fSym.render(sym,False,oc)
                self.board_surf.blit(ol,(x+SQ//2-ol.get_width()//2+dx,y+SQ//2-ol.get_height()//2+dy))
            lbl=self.fSym.render(sym,False,wc)
            self.board_surf.blit(lbl,(x+SQ//2-lbl.get_width()//2,y+SQ//2-lbl.get_height()//2))
        elif style=='Lettres':
            letter=PIECE_LETTER[kind]
            pygame.draw.circle(self.board_surf,oc,(x+SQ//2,y+SQ//2),SQ//2-6)
            pygame.draw.circle(self.board_surf,wc,(x+SQ//2,y+SQ//2),SQ//2-8)
            lbl=self.fM.render(letter,False,oc)
            self.board_surf.blit(lbl,(x+SQ//2-lbl.get_width()//2,y+SQ//2-lbl.get_height()//2))
        elif style=='Mini':
            sym=PIECE_CHARS_FILLED[p]
            pygame.draw.circle(self.board_surf,oc,(x+SQ//2,y+SQ//2),SQ//2-4)
            pygame.draw.circle(self.board_surf,wc,(x+SQ//2,y+SQ//2),SQ//2-6)
            lbl=self.fSymS.render(sym,False,oc)
            self.board_surf.blit(lbl,(x+SQ//2-lbl.get_width()//2,y+SQ//2-lbl.get_height()//2))

    def _draw_puzzle_banner(self,game,T):
        pz=game.puzzles[game.puzzle_index]
        if game.puzzle_status=='solved': msg="✔ Résolu !"; bg=(30,110,50)
        elif game.puzzle_status=='wrong': msg="✘ Incorrect, réessayez"; bg=(120,35,30)
        elif game.puzzle_status=='correct': msg="✔ Bien joué, continuez…"; bg=(30,90,110)
        else: msg=f"Puzzle {game.puzzle_index+1}/{len(game.puzzles)} — trouvez le meilleur coup"; bg=(40,40,30)
        surf=pygame.Surface((BOARD_SIZE,30),pygame.SRCALPHA)
        surf.fill((*bg,210))
        lbl=self.fS.render(msg,False,(240,240,230))
        surf.blit(lbl,(10,15-lbl.get_height()//2))
        self.screen.blit(surf,(BOARD_X,0))

    def _draw_graph(self,game,T):
        surf=self.graph_surf
        surf.fill(T['graph_bg'])
        hist=game.eval_history
        midy=GRAPH_H//2
        pygame.draw.line(surf,T['panel2'],(0,midy),(BOARD_SIZE,midy),1)
        if len(hist)>=2:
            maxabs=min(15.0,max(1.0,max(abs(v) for v in hist)))
            n=len(hist)
            pts=[]
            for i,v in enumerate(hist):
                x=int(i/(n-1)*(BOARD_SIZE-1))
                vv=max(-maxabs,min(maxabs,v))
                y=int(midy-(vv/maxabs)*(GRAPH_H//2-8))
                pts.append((x,y))
            pygame.draw.lines(surf,T['graph_line'],False,pts,2)
            cx,cy=pts[-1]
            marker=pts[game.replay_index] if game.replay_index is not None and game.replay_index<len(pts) else pts[-1]
            pygame.draw.circle(surf,T['accent'],marker,4)
        lbl=self.fXS.render("Évolution de l'évaluation",False,T['text_dim'])
        surf.blit(lbl,(6,3))
        self.screen.blit(surf,(BOARD_X,BOARD_SIZE))
        pygame.draw.rect(self.screen,T['accent'],(BOARD_X,BOARD_SIZE,BOARD_SIZE,GRAPH_H),1)

    def _draw_toast(self,game,T):
        if not game.status_message or time.time()>game.status_message_until: return
        lbl=self.fS.render(game.status_message,False,(20,20,15))
        pad=10; w=lbl.get_width()+2*pad; h=lbl.get_height()+2*pad
        x=BOARD_X+(BOARD_SIZE-w)//2; y=BOARD_SIZE-h-14
        surf=pygame.Surface((w,h),pygame.SRCALPHA); surf.fill((255,225,120,235))
        surf.blit(lbl,(pad,pad))
        self.screen.blit(surf,(x,y))

    # ---- panel building blocks ----
    def _section(self,T,title,y):
        pygame.draw.line(self.panel,T['panel2'],(self._x0,y),(PANEL_W-self._x0,y),1); y+=6
        lb=self.fS.render(title,False,T['accent']); self.panel.blit(lb,(self._x0,y)); y+=18
        return y

    def _button(self,T,label,key,y,x=None,w=None,toggled=False,enabled=True):
        x=self._x0 if x is None else x
        w=(PANEL_W-2*self._x0) if w is None else w
        rect=pygame.Rect(x,y,w,30)
        screen_rect=pygame.Rect(PANEL_X+x,y-self.scroll_y,w,30)
        self._buttons_layout[key]=screen_rect
        mx,my=pygame.mouse.get_pos()
        hov=enabled and screen_rect.collidepoint(mx,my)
        if not enabled: bc=T['panel2']
        elif toggled: bc=T['accent']
        else: bc=T['btn_hov'] if hov else T['btn']
        pygame.draw.rect(self.panel,bc,rect,border_radius=6)
        pygame.draw.rect(self.panel,T['accent'] if enabled else T['text_dim'],rect,1,border_radius=6)
        tc=T['panel_bg'] if toggled else (T['text'] if enabled else T['text_dim'])
        lb=self.fS.render(label,False,tc)
        self.panel.blit(lb,(x+w//2-lb.get_width()//2,y+15-lb.get_height()//2))
        return y+36

    def _button_pair(self,T,label1,key1,label2,key2,y,toggled1=False,toggled2=False,enabled1=True,enabled2=True):
        half=(PANEL_W-2*self._x0-8)//2
        self._button(T,label1,key1,y,x=self._x0,w=half,toggled=toggled1,enabled=enabled1)
        self._button(T,label2,key2,y,x=self._x0+half+8,w=half,toggled=toggled2,enabled=enabled2)
        return y+36

    def _grid(self,T,items,key_of,label_of,selected_of,y,cols,row_h=20,x0=None,pw=None):
        x0=self._x0 if x0 is None else x0
        pw=(PANEL_W-2*self._x0) if pw is None else pw
        cw=pw//cols
        for i,item in enumerate(items):
            col=i%cols; row=i//cols
            r=pygame.Rect(x0+col*cw,y+row*(row_h+2),cw-2,row_h)
            key=key_of(item)
            self._buttons_layout[key]=pygame.Rect(PANEL_X+r.x,r.y-self.scroll_y,r.w,r.h)
            sel=selected_of(item)
            bc=T['accent'] if sel else T['btn']
            pygame.draw.rect(self.panel,bc,r,border_radius=4)
            lb=self.fXS.render(label_of(item),False,T['panel_bg'] if sel else T['text'])
            self.panel.blit(lb,(r.x+r.w//2-lb.get_width()//2,r.y+row_h//2-lb.get_height()//2))
        rows=(len(items)+cols-1)//cols
        return y+rows*(row_h+2)

    def _edit_palette(self,T,game,y):
        """12-piece placement palette for edit mode: click a cell to arm that piece, then click
           squares on the board to stamp it there (any number of times)."""
        items=[(col,kind) for col in ('w','b') for kind in ('K','Q','R','B','N','P')]
        cols=6; cw=(PANEL_W-2*self._x0)//cols; row_h=28
        for i,(col,kind) in enumerate(items):
            c=i%cols; row=i//cols
            code=col+kind
            r=pygame.Rect(self._x0+c*cw,y+row*(row_h+2),cw-2,row_h)
            key=f"edit_piece_{code}"
            self._buttons_layout[key]=pygame.Rect(PANEL_X+r.x,r.y-self.scroll_y,r.w,r.h)
            sel=(game.edit_piece==code)
            bg=T['piece_w'] if col=='w' else T['piece_b']
            pygame.draw.rect(self.panel,bg,r,border_radius=4)
            pygame.draw.rect(self.panel,T['accent'] if sel else T['panel2'],r,3 if sel else 1,border_radius=4)
            tc=T['piece_b_out'] if col=='w' else T['piece_w_out']
            lb=self.fS.render(PIECE_LETTER[kind],False,tc)
            self.panel.blit(lb,(r.x+r.w//2-lb.get_width()//2,r.y+row_h//2-lb.get_height()//2))
        rows=(len(items)+cols-1)//cols
        return y+rows*(row_h+2)

    def _draw_panel(self,game,T):
        x0=14; self._x0=x0; pw=PANEL_W-2*x0
        self.panel.fill(T['panel_bg'])
        self._buttons_layout={}
        y=12

        t=self.fL.render("♟ ÉCHECS PRO",False,T['accent']); self.panel.blit(t,(x0,y)); y+=34

        _,turn_disp,status_disp=game.display_state()
        live=game.is_live()
        idx=game.replay_index if game.replay_index is not None else len(game.position_snapshots)-1

        if game.edit_mode:
            msg="✏️ Mode Édition — placez/déplacez librement"; sc=T['accent']
        elif not live:
            msg=f"Replay — position {idx}/{len(game.position_snapshots)-1}"; sc=T['accent']
        elif game.puzzle_mode:
            if game.puzzle_status=='solved': msg="Puzzle résolu ! 🎉"; sc=(90,220,110)
            elif game.puzzle_status=='wrong': msg="Incorrect — réessayez"; sc=(220,90,80)
            elif game.puzzle_status=='correct': msg="Bien joué, continuez…"; sc=(90,200,220)
            else: msg=f"Puzzle {game.puzzle_index+1}/{len(game.puzzles)}"; sc=T['text']
        elif status_disp=='checkmate':
            msg="Échec et mat !"; sc=(220,60,60)
        elif status_disp=='stalemate':
            msg="Pat — nulle"; sc=(200,200,60)
        elif status_disp=='draw_repetition':
            msg="Nulle — répétition triple"; sc=(200,200,60)
        elif status_disp=='draw_50move':
            msg="Nulle — règle des 50 coups"; sc=(200,200,60)
        elif status_disp=='timeout_w':
            msg="Temps écoulé — Blancs perdent"; sc=(220,60,60)
        elif status_disp=='timeout_b':
            msg="Temps écoulé — Noirs perdent"; sc=(220,60,60)
        elif status_disp=='check':
            msg="ÉCHEC AU ROI !"; sc=(230,100,40)
        elif game.ai_thinking:
            dots="."*(1+int(self._anim_t*2)%4)
            msg=f"IA réfléchit{dots}"; sc=T['text_dim']
        else:
            msg=f"Tour des {game.col_name(turn_disp)}"; sc=T['text']
        lm=self.fM.render(msg,False,sc); self.panel.blit(lm,(x0,y)); y+=24

        eval_now=game.eval_history[idx] if idx<len(game.eval_history) else game.eval_history[-1]
        ec=(90,220,110) if eval_now>0.15 else ((220,90,80) if eval_now<-0.15 else T['text_dim'])
        le=self.fM.render(f"Éval : {eval_now:+.2f}",False,ec)
        self.panel.blit(le,(x0,y)); y+=22

        if game.puzzle_mode:
            desc=game.puzzles[game.puzzle_index].get('description','')
            ld=self.fXS.render(desc,False,T['text_dim']); self.panel.blit(ld,(x0,y)); y+=16

        engine_name="Stockfish" if (game.stockfish and game.use_stockfish) else "moteur interne"
        mode_txt={"pvp":"2 Joueurs","vs_ai":"Joueur vs IA","puzzle":"Puzzle"}[game.mode]
        lmode=self.fXS.render(f"Mode: {mode_txt}",False,T['text_dim']); self.panel.blit(lmode,(x0,y)); y+=14
        if game.mode=='vs_ai':
            lvl=["Facile","Normal","Fort","Expert","Maître"][min(max(game.ai_depth-2,0),4)]
            ll=self.fXS.render(f"Niveau: {lvl} ({engine_name}) | IA = {game.col_name(game.ai_color)}",False,T['text_dim'])
            self.panel.blit(ll,(x0,y)); y+=14
        y+=4

        if game.chrono_enabled and not game.puzzle_mode:
            y=self._section(T,"Chrono",y)
            for col,val in (('w',game.clock_w),('b',game.clock_b)):
                active=(turn_disp==col and live and status_disp in ('playing','check'))
                mm=int(val)//60; ss=int(val)%60
                low=val<10
                cc=(230,70,60) if low else (T['accent'] if active else T['text'])
                if active:
                    bg=pygame.Rect(x0-4,y-2,pw+8,20)
                    pygame.draw.rect(self.panel,T['btn_hov'],bg,border_radius=4)
                lc=self.fM.render(f"{'●' if col=='w' else '○'} {game.col_name(col)}: {mm:02d}:{ss:02d}",False,cc)
                self.panel.blit(lc,(x0,y)); y+=22
            y+=4

        if game.ai_thinking:
            y=self._section(T,"Réflexion IA",y)
            info=game.ai_progress or {}
            depth=info.get('depth','?')
            elapsed=info.get('elapsed',0.0)
            frac=max(0.0,min(1.0,elapsed/3.0))
            bar_rect=pygame.Rect(x0,y,pw,14)
            pygame.draw.rect(self.panel,T['panel2'],bar_rect,border_radius=6)
            pygame.draw.rect(self.panel,T['accent'],pygame.Rect(x0,y,int(pw*frac),14),border_radius=6)
            pygame.draw.rect(self.panel,T['text_dim'],bar_rect,1,border_radius=6)
            y+=18
            cand_uci=info.get('candidate_uci')
            cand=info.get('candidate') or info.get('best_move')
            cand_txt=cand_uci if cand_uci else self._move_label(cand)
            best_eval=info.get('best_eval')
            if isinstance(best_eval,(int,float)) and info.get('engine')!='stockfish':
                eval_txt=f"{best_eval/100.0:+.2f}"
            elif info.get('score_type')=='cp':
                eval_txt=f"{info.get('score_val',0)/100.0:+.2f}"
            elif info.get('score_type')=='mate':
                eval_txt=f"#{info.get('score_val')}"
            else:
                eval_txt='—'
            ltxt=self.fXS.render(f"Profondeur {depth} | coup: {cand_txt or '…'} | éval {eval_txt}",False,T['text_dim'])
            self.panel.blit(ltxt,(x0,y)); y+=18
            y+=2

        if game.top_moves:
            title="Top 3 coups (analyse)" if game.top_moves_source=='analysis' else "Top 3 coups suggérés"
            y=self._section(T,title,y)
            for i,(mv,ev,san) in enumerate(game.top_moves):
                col=(255,225,120) if i==0 else T['text_dim']
                lt=self.fXS.render(f"{i+1}. {san}   ({ev:+.2f})",False,col)
                self.panel.blit(lt,(x0,y)); y+=15
            y+=4

        y=self._section(T,"Actions",y)
        y=self._button(T,"🔄 Nouvelle Partie",'new',y)
        y=self._button(T,"↩ Annuler le coup (Ctrl+Z)",'undo',y,enabled=not game.puzzle_mode)
        y=self._button(T,"💡 Meilleurs coups (H)",'hint',y)
        y=self._button(T,"🔁 Retourner le plateau",'flip',y)
        y=self._button(T,f"✏️ Mode Édition : {'ON ✓' if game.edit_mode else 'OFF'}",'toggle_edit',y,toggled=game.edit_mode)
        if game.edit_mode:
            y=self._edit_palette(T,game,y)
            y=self._button(T,"🧹 Effacer (outil)",'edit_erase',y,toggled=(game.edit_piece=='erase'))
            y=self._button(T,"✋ Déplacer librement",'edit_move_tool',y,toggled=(game.edit_piece is None))
            y=self._button_pair(T,"⚪ Trait: Blancs",'edit_turn_w',"⚫ Trait: Noirs",'edit_turn_b',y,
                                 toggled1=(game.turn=='w'),toggled2=(game.turn=='b'))
            y=self._button_pair(T,"🗑 Vider","edit_clear","♟ Position initiale",'edit_start',y)
            y=self._button(T,"🎯 Meilleur coup",'edit_best_move',y)
            y+=4

        y=self._section(T,"Replay (←/→, Échap=direct)",y)
        lrep=self.fXS.render(f"Position {idx}/{len(game.position_snapshots)-1}"+("" if not live else "  (direct)"),False,T['text_dim'])
        self.panel.blit(lrep,(x0,y)); y+=16
        y=self._button_pair(T,"◀ Précédent",'replay_prev',"Suivant ▶",'replay_next',y,
                             enabled1=idx>0,enabled2=idx<len(game.position_snapshots)-1)
        if not live:
            y=self._button(T,"⏺ Revenir au direct",'replay_live',y)
        y+=2

        y=self._section(T,"Modes de jeu",y)
        y=self._grid(T,[('2 Joueurs','pvp'),('vs IA','ai'),('Puzzle','puzzle')],
                      lambda it:f"mode_{it[1]}",lambda it:it[0],
                      lambda it:(game.mode=='pvp' and it[1]=='pvp') or (game.mode=='vs_ai' and it[1]=='ai') or (game.mode=='puzzle' and it[1]=='puzzle'),
                      y,3)
        y+=4
        y=self._button(T,f"🔍 Mode Analyse : {'ON ✓' if game.analysis_mode else 'OFF'}",'toggle_analysis',y,toggled=game.analysis_mode)
        y=self._button(T,f"🙈 Blind Chess : {'ON ✓' if game.blind_mode else 'OFF'}",'toggle_blind',y,toggled=game.blind_mode)
        y=self._button(T,f"⏱ Chrono : {'ON ✓' if game.chrono_enabled else 'OFF'}",'toggle_chrono',y,toggled=game.chrono_enabled)
        y=self._grid(T,CLOCK_PRESETS,lambda it:f"clock_{it[1]}",lambda it:it[0],
                      lambda it:game.clock_initial==it[1],y,4)
        y+=4

        if game.mode=='puzzle':
            y=self._section(T,"Puzzle",y)
            y=self._button_pair(T,"◀ Puzzle préc.",'puzzle_prev',"Puzzle suiv. ▶",'puzzle_next',y)
            y=self._button(T,"✖ Quitter le mode puzzle",'puzzle_exit',y)
            y+=2

        y=self._section(T,"Difficulté IA",y)
        diff_labels=["Facile","Normal","Fort","Expert","Maître"]; diff_depths=[2,3,4,5,6]
        y=self._grid(T,list(zip(diff_labels,diff_depths)),lambda it:f"diff_{it[1]}",lambda it:it[0],
                      lambda it:game.ai_depth==it[1],y,5)
        if game.stockfish:
            y+=4
            y=self._button(T,f"♞ Stockfish : {'ON ✓' if game.use_stockfish else 'OFF (interne)'}",'toggle_stockfish',y,toggled=game.use_stockfish)
        y+=2

        y=self._section(T,"Thème",y)
        y=self._grid(T,list(enumerate(THEME_NAMES)),lambda it:f"theme_{it[0]}",lambda it:it[1],
                      lambda it:game.theme_idx==it[0],y,3)
        y+=4
        y=self._section(T,"Style pièces",y)
        y=self._grid(T,list(enumerate(PIECE_STYLES)),lambda it:f"pstyle_{it[0]}",lambda it:it[1],
                      lambda it:game.piece_style_idx==it[0],y,3)
        y+=4

        y=self._section(T,"Position & Export",y)
        y=self._button_pair(T,"📋 Charger FEN",'fen_load',"💾 Sauver FEN",'fen_save',y)
        y=self._button(T,"📤 Export PGN",'export_pgn',y,enabled=len(game.san_history)>0)
        y+=2

        y=self._section(T,f"Historique ({len(game.san_history)} coups)",y)
        for i in range(0,len(game.san_history),2):
            num=i//2+1
            wtxt=game.san_history[i]
            btxt=game.san_history[i+1] if i+1<len(game.san_history) else ''
            highlight=(not live and idx-1 in (i,i+1)) or (live and i>=len(game.san_history)-2)
            lc=T['text'] if highlight else T['text_dim']
            lh=self.fXS.render(f"{num}. {wtxt}  {btxt}",False,lc)
            self.panel.blit(lh,(x0,y)); y+=15
        y+=10

        self._panel_content_h=y+10
        self.screen.blit(self.panel,(PANEL_X,-self.scroll_y))

    def _draw_promotion(self,game,T):
        fr,fc,tr,tc=game.promotion_pending
        col=col_of(game.board[fr][fc])
        choices=['Q','R','B','N']
        pad=10; total=len(choices)*(SQ+pad)-pad
        ox=BOARD_X+(BOARD_SIZE-total)//2; oy=(BOARD_SIZE-SQ)//2
        ov=pygame.Surface((W,H),pygame.SRCALPHA)
        ov.fill((0,0,0,160)); self.screen.blit(ov,(0,0))
        bx=ox-22; bw=total+44; bh=SQ+70
        pygame.draw.rect(self.screen,T['panel_bg'],(bx,oy-36,bw,bh),border_radius=14)
        pygame.draw.rect(self.screen,T['accent'],(bx,oy-36,bw,bh),2,border_radius=14)
        tl=self.fM.render("Choisir la pièce",False,T['text'])
        self.screen.blit(tl,(bx+bw//2-tl.get_width()//2,oy-30))
        self._promo_rects=[]
        for i,k in enumerate(choices):
            rx=ox+i*(SQ+pad); ry=oy+16
            pygame.draw.rect(self.screen,T['btn'],(rx,ry,SQ,SQ),border_radius=8)
            pygame.draw.rect(self.screen,T['panel2'],(rx,ry,SQ,SQ),1,border_radius=8)
            p=col+k; wc=T['piece_w'] if col=='w' else T['piece_b']
            sym=PIECE_CHARS_FILLED[p]
            lb=self.fSymB.render(sym,False,wc)
            self.screen.blit(lb,(rx+SQ//2-lb.get_width()//2,ry+SQ//2-lb.get_height()//2))
            nl=self.fXS.render(PIECE_LABEL[k],False,T['text_dim'])
            self.screen.blit(nl,(rx+SQ//2-nl.get_width()//2,ry+SQ+2))
            self._promo_rects.append((rx,ry,SQ,SQ,k))

    def _draw_fen_modal(self,game,T):
        ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,170)); self.screen.blit(ov,(0,0))
        bw,bh=580,140
        bx,by=BOARD_X+(BOARD_SIZE-bw)//2,(BOARD_SIZE-bh)//2
        pygame.draw.rect(self.screen,T['panel_bg'],(bx,by,bw,bh),border_radius=12)
        pygame.draw.rect(self.screen,T['accent'],(bx,by,bw,bh),2,border_radius=12)
        tl=self.fM.render("Charger une position FEN",False,T['text'])
        self.screen.blit(tl,(bx+16,by+12))
        box=pygame.Rect(bx+16,by+46,bw-32,32)
        pygame.draw.rect(self.screen,T['panel2'],box,border_radius=6)
        pygame.draw.rect(self.screen,T['accent'],box,1,border_radius=6)
        txt=game.fen_input_text
        cursor="│" if int(self._anim_t*2)%2==0 else ""
        lt=self.fXS.render(txt+cursor,False,T['text'])
        self.screen.blit(lt,(box.x+8,box.y+box.h//2-lt.get_height()//2))
        hint=self.fXS.render("Entrée = charger   Échap = annuler",False,T['text_dim'])
        self.screen.blit(hint,(bx+16,by+bh-24))

    def get_buttons(self): return getattr(self,'_buttons_layout',{})
    def get_promo_rects(self): return getattr(self,'_promo_rects',[])

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def handle_button(game,key):
    if key=='new': game.reset()
    elif key=='undo': game.undo()
    elif key=='hint': game.start_hint()
    elif key=='flip': game.flip=not game.flip
    elif key=='toggle_edit': game.toggle_edit_mode()
    elif key=='edit_erase':
        game.edit_piece=None if game.edit_piece=='erase' else 'erase'
        game.edit_selected=None
    elif key=='edit_move_tool':
        game.edit_piece=None; game.edit_selected=None
    elif key.startswith('edit_piece_'):
        code=key.split('_',2)[2]
        game.edit_piece=None if game.edit_piece==code else code
        game.edit_selected=None
    elif key=='edit_turn_w': game.turn='w'
    elif key=='edit_turn_b': game.turn='b'
    elif key=='edit_clear': game.edit_clear_board()
    elif key=='edit_start': game.edit_reset_start()
    elif key=='edit_best_move': game.start_analysis()
    elif key=='replay_prev': game.replay_step(-1)
    elif key=='replay_next': game.replay_step(1)
    elif key=='replay_live': game.enter_replay(len(game.position_snapshots)-1)
    elif key=='mode_pvp':
        if game.puzzle_mode: game.exit_puzzle()
        game.mode='pvp'
    elif key=='mode_ai':
        if game.puzzle_mode: game.exit_puzzle()
        game.mode='vs_ai'; game.ai_color='b'
    elif key=='mode_puzzle':
        game.load_puzzle(game.puzzle_index)
    elif key=='toggle_analysis':
        game.analysis_mode=not game.analysis_mode
    elif key=='toggle_blind':
        game.blind_mode=not game.blind_mode
        if game.blind_mode:
            if game.puzzle_mode: game.exit_puzzle()
            game.mode='vs_ai'
    elif key=='toggle_chrono':
        game.chrono_enabled=not game.chrono_enabled
        if game.chrono_enabled: game.set_clock_preset(game.clock_initial)
    elif key.startswith('clock_'):
        game.set_clock_preset(int(key.split('_')[1]))
    elif key=='puzzle_prev': game.load_puzzle(game.puzzle_index-1)
    elif key=='puzzle_next': game.load_puzzle(game.puzzle_index+1)
    elif key=='puzzle_exit': game.exit_puzzle()
    elif key.startswith('diff_'): game.ai_depth=int(key.split('_')[1])
    elif key=='toggle_stockfish': game.use_stockfish=not game.use_stockfish
    elif key.startswith('theme_'): game.theme_idx=int(key.split('_')[1])
    elif key.startswith('pstyle_'): game.piece_style_idx=int(key.split('_')[1])
    elif key=='fen_load':
        game.fen_input_active=True; game.fen_input_text=game.current_fen()
    elif key=='fen_save': game.save_fen_to_file()
    elif key=='export_pgn': game.export_pgn()

async def main():
    pygame.init()
    screen=pygame.display.set_mode((W,H))
    pygame.display.set_caption("Échecs Pro")
    renderer=Renderer(screen)
    game=Game()
    clock=pygame.time.Clock()
    last_time=time.time()

    try:
        while True:
            now=time.time(); dt=now-last_time; last_time=now
            game.tick_clock(dt)

            if not game.edit_mode and game.mode=='vs_ai' and game.turn==game.ai_color and game.is_live() \
               and not game.ai_thinking and game.status in ('playing','check') and game.ai_result is None:
                game.start_ai_move()
            if game.ai_result is not None:
                game.apply_ai_result()

            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    raise SystemExit

                if event.type==pygame.KEYDOWN:
                    if game.fen_input_active:
                        if event.key==pygame.K_RETURN:
                            try:
                                game.load_fen(game.fen_input_text.strip())
                                game.flash("Position chargée.",2.0)
                            except Exception as ex:
                                game.flash(f"FEN invalide : {ex}",3.0)
                            game.fen_input_active=False
                        elif event.key==pygame.K_ESCAPE:
                            game.fen_input_active=False
                        elif event.key==pygame.K_BACKSPACE:
                            game.fen_input_text=game.fen_input_text[:-1]
                        elif event.unicode and event.unicode.isprintable():
                            game.fen_input_text+=event.unicode
                        continue
                    if event.key==pygame.K_z and (event.mod & pygame.KMOD_CTRL): game.undo()
                    elif event.key==pygame.K_h: game.start_hint()
                    elif event.key==pygame.K_n: game.reset()
                    elif event.key==pygame.K_LEFT: game.replay_step(-1)
                    elif event.key==pygame.K_RIGHT: game.replay_step(1)
                    elif event.key==pygame.K_ESCAPE and not game.is_live():
                        game.enter_replay(len(game.position_snapshots)-1)

                if event.type==pygame.MOUSEWHEEL:
                    mx,my=pygame.mouse.get_pos()
                    if mx>=PANEL_X:
                        renderer.scroll_y-=event.y*30
                        maxscroll=max(0,renderer._panel_content_h-H)
                        renderer.scroll_y=max(0,min(renderer.scroll_y,maxscroll))

                if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                    mx,my=event.pos
                    if game.fen_input_active:
                        continue
                    if game.promotion_pending:
                        for rx,ry,rw,rh,k in renderer.get_promo_rects():
                            if rx<=mx<rx+rw and ry<=my<ry+rh: game.promote(k)
                        continue
                    btns=renderer.get_buttons()
                    clicked=False
                    for key,rect in btns.items():
                        if rect.collidepoint(mx,my):
                            clicked=True
                            handle_button(game,key)
                            break
                    if clicked: continue
                    if BOARD_X<=mx<BOARD_X+BOARD_SIZE:
                        c=(mx-BOARD_X)//SQ; r=my//SQ
                        if game.flip: r,c=7-r,7-c
                        if 0<=r<8 and 0<=c<8:
                            if game.edit_mode: game.edit_click(r,c)
                            elif game.is_live(): game.click(r,c)

            renderer.draw(game,dt)
            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)   # yield to the browser's event loop (no-op on desktop)
    finally:
        if game.stockfish: game.stockfish.close()
        pygame.quit()

if __name__=='__main__':
    asyncio.run(main())
