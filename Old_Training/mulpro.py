from concurrent.futures import ProcessPoolExecutor
import math, time

def heavy(x):
    # heavy CPU work
    s = 0.0
    for i in range(1, 2000000):
        s += math.sin(i + x)
    return s

if __name__ == "__main__":
    inputs = list(range(8))  # 8 tasks
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=4) as exe:  # spawn processes (use number of cores)
        results = list(exe.map(heavy, inputs))
    print("elapsed:", time.time() - t0)
