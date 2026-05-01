import random
import time
import copy
from collections import deque

from src.utils import _adj, _lbl, cout_total
from src.marche_pied import calculer_potentiels, trouver_cycle_pour_arete
from src.balas_hammer import _calculer_penalites  


# ============================================================
#  13. ETUDE DE COMPLEXITE
# ============================================================

def generer_probleme_aleatoire(n):
    """
    Genere un probleme equilibre de taille n x n.
    Les provisions et commandes sont construites via une matrice temp
    telle que sum(Pi) = sum(Cj).
    """
    A    = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
    temp = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
    provisions = [sum(temp[i])            for i in range(n)]
    commandes  = [sum(temp[i][j] for i in range(n)) for j in range(n)]
    return A, provisions, commandes


# --- Versions silencieuses (sans print) pour les mesures ---

def _no_silent(n, m, provisions, commandes):
    prov = list(provisions); comm = list(commandes)
    prop = [[0]*m for _ in range(n)]; base = set()
    i, j = 0, 0
    while i < n and j < m:
        val = min(prov[i], comm[j])
        prop[i][j] = val; base.add((i, j))
        prov[i] -= val; comm[j] -= val
        if prov[i] == 0 and comm[j] == 0:
            i += 1
            if i < n and j + 1 < m: j += 1
        elif prov[i] == 0: i += 1
        else: j += 1
    return prop, base


def _bh_silent(n, m, A, provisions, commandes):
    prov = list(provisions); comm = list(commandes)
    prop = [[0]*m for _ in range(n)]; base = set()
    lf = [False]*n; cf = [False]*m
    while True:
        if all(p == 0 for p in prov) or all(c == 0 for c in comm): break
        pl, pc = _calculer_penalites(n, m, A, prov, comm, lf, cf)
        max_p = -1; best = None
        for i in range(n):
            if pl[i] is not None and pl[i] > max_p: max_p = pl[i]; best = ('L', i)
        for j in range(m):
            if pc[j] is not None and pc[j] > max_p: max_p = pc[j]; best = ('C', j)
        if best is None: break
        if best[0] == 'L':
            i_s = best[1]
            cols = [j for j in range(m) if not cf[j] and comm[j] > 0]
            if not cols: break
            j_s = min(cols, key=lambda j: A[i_s][j])
        else:
            j_s = best[1]
            ligs = [i for i in range(n) if not lf[i] and prov[i] > 0]
            if not ligs: break
            i_s = min(ligs, key=lambda i: A[i][j_s])
        val = min(prov[i_s], comm[j_s])
        prop[i_s][j_s] += val; base.add((i_s, j_s))
        prov[i_s] -= val; comm[j_s] -= val
        if prov[i_s] == 0: lf[i_s] = True
        if comm[j_s] == 0: cf[j_s] = True
    return prop, base


def _mp_silent(n, m, A, prop_init, base_init, provisions, commandes):
    """Marche-pied sans affichage pour mesure de performance."""
    prop = copy.deepcopy(prop_init)
    base = set(base_init)
    for _ in range(500):
        # Correction degenerescence (silencieuse)
        for __ in range(200):
            g = _adj(n, m, base)
            visite = {}; parent = {}; cycle = None
            for start in range(n + m):
                if start in visite or not g[start]: continue
                queue = deque([start]); visite[start] = True; parent[start] = -1
                found = False
                while queue and not found:
                    u = queue.popleft()
                    for v in g[u]:
                        if v not in visite:
                            visite[v] = True; parent[v] = u; queue.append(v)
                        elif v != parent[u]:
                            ch_u = []; x = u
                            while x != -1: ch_u.append(x); x = parent[x]
                            ch_v = []; x = v
                            while x != -1: ch_v.append(x); x = parent[x]
                            su = {nd: i for i, nd in enumerate(ch_u)}
                            anc = next((nd for nd in ch_v if nd in su), None)
                            if anc is None:
                                cycle = ch_u + [v]
                            else:
                                cycle = ch_u[:su[anc]+1] + list(reversed(ch_v[:ch_v.index(anc)]))
                            found = True; break
                if found: break
            if cycle is None: break
            paires = []
            for k in range(len(cycle)-1):
                u2, v2 = cycle[k], cycle[k+1]
                if u2 < n and v2 >= n: paires.append((u2, v2-n))
                elif v2 < n and u2 >= n: paires.append((v2, u2-n))
            mc = paires[1::2]
            if not mc: break
            delta = min(prop[i][j] for i, j in mc)
            for i, j in paires[0::2]: prop[i][j] += delta; base.add((i, j))
            for i, j in mc:
                prop[i][j] -= delta
                if prop[i][j] == 0: base.discard((i, j))
        # Connexite silencieuse
        actifs = set(k for k in range(n+m) if _adj(n, m, base)[k])
        if actifs:
            vis2 = set(); q2 = deque([next(iter(actifs))]); vis2.add(next(iter(actifs)))
            while q2:
                u2 = q2.popleft()
                for v2 in _adj(n, m, base)[u2]:
                    if v2 not in vis2: vis2.add(v2); q2.append(v2)
            if vis2 != actifs:
                cases = sorted(((A[i][j], i, j) for i in range(n) for j in range(m)
                                if (i, j) not in base), key=lambda x: x[0])
                for _, i, j in cases:
                    tb = base | {(i, j)}
                    act2 = set(k for k in range(n+m) if _adj(n, m, tb)[k])
                    v2s = set(); q3 = deque([next(iter(act2))]); v2s.add(next(iter(act2)))
                    while q3:
                        u3 = q3.popleft()
                        for v3 in _adj(n, m, tb)[u3]:
                            if v3 not in v2s: v2s.add(v3); q3.append(v3)
                    if v2s == act2: base.add((i, j)); prop[i][j] = 0; break
        # Potentiels et marginaux
        u, v = calculer_potentiels(n, m, A, base)
        best = None; bv = 0
        for i in range(n):
            for j in range(m):
                if (i, j) not in base:
                    mg = A[i][j] - u[i] - v[j]
                    if mg < bv: bv = mg; best = (i, j)
        if best is None: break
        i_s, j_s = best
        cycle2 = trouver_cycle_pour_arete(n, m, base, i_s, j_s)
        prop[i_s][j_s] = 0; base.add((i_s, j_s))
        paires2 = []
        for k in range(len(cycle2)-1):
            u2, v2 = cycle2[k], cycle2[k+1]
            if u2 < n and v2 >= n: paires2.append((u2, v2-n))
            elif v2 < n and u2 >= n: paires2.append((v2, u2-n))
        if (i_s, j_s) in paires2:
            idx = paires2.index((i_s, j_s))
            paires2 = paires2[idx:] + paires2[:idx]
        mc2 = paires2[1::2]
        if mc2:
            delta2 = min(prop[i][j] for i, j in mc2)
            for i, j in paires2[0::2]: prop[i][j] += delta2; base.add((i, j))
            for i, j in mc2:
                prop[i][j] -= delta2
                if prop[i][j] == 0: base.discard((i, j))
    return prop, base


def etude_complexite():
    """
    Mesure les temps d'execution de NO, BH et Marche-Pied sur des problemes aleatoires.
    Trace les nuages de points et enveloppes superieures.
    """
    try:
        import matplotlib.pyplot as plt
        HAS_PLOT = True
    except ImportError:
        print("matplotlib non disponible.")
        HAS_PLOT = False

    valeurs_n = [10, 40, 100, 400]   # Pour l'etude complete : [10, 40, 100, 400, 1000, 4000, 10000]
    nb_rep = 10                        # Pour l'etude complete : 100

    res = {
        'theta_NO': {n: [] for n in valeurs_n},
        'theta_BH': {n: [] for n in valeurs_n},
        't_NO':     {n: [] for n in valeurs_n},
        't_BH':     {n: [] for n in valeurs_n},
    }

    for n in valeurs_n:
        print(f"\n  Taille n={n} ...")
        for _ in range(nb_rep):
            A, prov, comm = generer_probleme_aleatoire(n)

            t0 = time.perf_counter()
            prop_no, base_no = _no_silent(n, n, prov, comm)
            res['theta_NO'][n].append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            prop_bh, base_bh = _bh_silent(n, n, A, prov, comm)
            res['theta_BH'][n].append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            _mp_silent(n, n, A, prop_no, base_no, prov, comm)
            res['t_NO'][n].append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            _mp_silent(n, n, A, prop_bh, base_bh, prov, comm)
            res['t_BH'][n].append(time.perf_counter() - t0)

    print("\n  === ENVELOPPES SUPERIEURES (pire des cas) ===")
    for key in res:
        print(f"\n  {key}:")
        for n in valeurs_n:
            vals = res[key][n]
            print(f"    n={n:5d}  max={max(vals):.6f}s  moy={sum(vals)/len(vals):.6f}s")

    if HAS_PLOT:
        _tracer_nuages(valeurs_n, res)


def _tracer_nuages(valeurs_n, res):
    import matplotlib.pyplot as plt
    series = [
        ('theta_NO', 'theta_NO (Nord-Ouest)'),
        ('theta_BH', 'theta_BH (Balas-Hammer)'),
        ('t_NO',     't_NO (Marche-pied / NO)'),
        ('t_BH',     't_BH (Marche-pied / BH)'),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Etude de complexite - Probleme de transport", fontsize=14)

    def plot_s(ax, key, title):
        for n in valeurs_n:
            ax.scatter([n]*len(res[key][n]), res[key][n], alpha=0.4, s=10, color='steelblue')
        ax.plot(valeurs_n, [max(res[key][n]) for n in valeurs_n], 'r-o', label='Enveloppe sup.')
        ax.set_title(title); ax.set_xlabel('n'); ax.set_ylabel('Temps (s)'); ax.legend()

    for idx, (key, title) in enumerate(series):
        plot_s(axes[idx//3][idx%3], key, title)

    for ax, key1, key2, title, color in [
        (axes[1][1], 'theta_NO', 't_NO', '(theta_NO + t_NO)', 'green'),
        (axes[1][2], 'theta_BH', 't_BH', '(theta_BH + t_BH)', 'orange'),
    ]:
        for n in valeurs_n:
            vals = [res[key1][n][k] + res[key2][n][k] for k in range(len(res[key1][n]))]
            ax.scatter([n]*len(vals), vals, alpha=0.4, s=10, color=color)
        mx = [max(res[key1][n][k]+res[key2][n][k] for k in range(len(res[key1][n])))
              for n in valeurs_n]
        ax.plot(valeurs_n, mx, 'r-o'); ax.set_title(title); ax.set_xlabel('n')

    plt.tight_layout()
    plt.savefig("complexite.png", dpi=150)
    print("\n  Graphe sauvegarde : complexite.png")
    plt.show()
