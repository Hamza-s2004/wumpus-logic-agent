from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

GRID_SIZE = 6

# hazards
pits = set()
for _ in range(5):
    p = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
    if p != (0,0):
        pits.add(p)

wumpus = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))

# Knowledge Base (CNF clauses)
KB = []

# ---------- helpers ----------
def neighbors(x,y):
    moves = [(1,0),(-1,0),(0,1),(0,-1)]
    res = []
    for dx,dy in moves:
        nx,ny = x+dx,y+dy
        if 0<=nx<GRID_SIZE and 0<=ny<GRID_SIZE:
            res.append((nx,ny))
    return res

def percept(x,y):
    breeze = any(n in pits for n in neighbors(x,y))
    stench = any(n == wumpus for n in neighbors(x,y))
    return breeze, stench

# ---------- encoding ----------
def pit_literal(x,y):
    return (x*10 + y + 1)

def wumpus_literal(x,y):
    return (x*10 + y + 100)

# ---------- KB update ----------
def update_kb(x,y,breeze,stench):
    neigh = neighbors(x,y)

    # Breeze
    if breeze:
        KB.append([pit_literal(nx,ny) for nx,ny in neigh])
    else:
        for nx,ny in neigh:
            KB.append([-pit_literal(nx,ny)])

    # Stench
    if stench:
        KB.append([wumpus_literal(nx,ny) for nx,ny in neigh])
    else:
        for nx,ny in neigh:
            KB.append([-wumpus_literal(nx,ny)])

# ---------- resolution ----------
def resolve(ci, cj):
    resolvents = []
    for di in ci:
        if -di in cj:
            new_clause = list(set(ci + cj))
            new_clause.remove(di)
            new_clause.remove(-di)
            resolvents.append(new_clause)
    return resolvents

def pl_resolution(kb, query):
    clauses = kb + [[-query]]
    new = []
    steps = 0

    while True:
        steps += 1
        pairs = [(clauses[i], clauses[j])
                 for i in range(len(clauses))
                 for j in range(i+1, len(clauses))]

        for (ci, cj) in pairs:
            resolvents = resolve(ci, cj)
            for r in resolvents:
                if r == []:
                    return True, steps
                if r not in new:
                    new.append(r)

        if all(r in clauses for r in new):
            return False, steps

        clauses.extend(new)

# ---------- safety ----------
def is_safe_by_logic(x,y):
    pit_lit = pit_literal(x,y)
    w_lit = wumpus_literal(x,y)

    safe_pit, s1 = pl_resolution(KB, -pit_lit)
    safe_w, s2 = pl_resolution(KB, -w_lit)

    return (safe_pit and safe_w), (s1+s2)

# ---------- API ----------
@app.route("/check", methods=["POST"])
def check():
    data = request.json
    x,y = data["x"], data["y"]

    breeze, stench = percept(x,y)

    # update KB from percepts
    update_kb(x,y,breeze,stench)

    # logical decision
    safe_logic, steps = is_safe_by_logic(x,y)

    return jsonify({
        "safe": safe_logic,
        "breeze": breeze,
        "stench": stench,
        "steps": steps
    })

if __name__ == "__main__":
    app.run(debug=True)