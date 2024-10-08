import math, random, numpy, pandas

#--Initialize Parameters---
n = 20 # Population Size
pc = 0.25 # Crossover Rate
pm = 0.01 # Mutation Rate
accurate = 1

def target_function(x, y):
    x_float = float(x)
    y_float = float(y)
    return 21.5 + x_float * math.sin(4 * 3.14 * x_float) + y_float * math.sin(20 * 3.14 * y_float) # Function

#--Initialize Population---
lst_x = [-3.0, 12.1]
lst_y = [4.1, 5.8]

len_x = round(math.log2((lst_x[1] - lst_x[0]) / accurate))
len_y = round(math.log2((lst_y[1] - lst_y[0]) / accurate))

bits_num =  len_x + len_y

g = numpy.zeros((n, bits_num))
for i in range(n):
    for j in range(bits_num):
        if random.randint(0, 1) < 0.5:
            g[i][j] = 0
        else:
            g[i][j] = 1
        g[i][j] = int(g[i][j].tolist())


# --Decode Chromosome--
def decoder(g, lst, length, is_x):
    decoded_values = []
    n = len(g)  
    for i in range(n):
        result = 0
        bina_to_dec = 0
        for j in range(length):
            if is_x:
                bina_to_dec += g[i][j] * pow(2, length - j - 1)
            else:
                bina_to_dec += g[i][length + j] * pow(2, length - j - 1)
        result = lst[0] + ((lst[1] - lst[0]) / (pow(2, length) - 1)) * bina_to_dec
        decoded_values.append(round(result, 2))
    return decoded_values


# Evaluate Selection Probability
def calculate_values(x, y):
    f = []
    p = []
    s = []
    num = []
    sum_func = 0
    cumulative_sum = 0
    
    f = [round(target_function(x[i],y[i]),2) for i in range(n)]
    sum_func = sum(f)

    for i in range(n):
        p.append(round(f[i] / sum_func, 3))
        cumulative_sum += p[i]
        s.append(round(cumulative_sum,2))
        num.append(n * p[i])

    return f, sum_func, p, s, num


def get_value(g):
    encoded_x = decoder(g, lst_x, len_x, True)
    encoded_y = decoder(g, lst_y, len_y, False)
    func, sum_func, p, s, num = calculate_values(encoded_x, encoded_y)
    return encoded_x,encoded_y,func,p,s,num

def check(n):
    if (n % 2 == 0):
        return n
    else:
        return n + 1

def new_population(g):
    expect_number = get_value(g)[5]
    max_index = numpy.argmax(expect_number)
    min_index = numpy.argmin(expect_number)
    print(f"Xoa min: {g[min_index]} co N: {expect_number[min_index]} thay vao la max: {g[max_index]} co N: {expect_number[max_index]}")
    g[min_index] = g[max_index].copy()
    sorted_indices = numpy.argsort(expect_number)[::-1] 
    global n 
    n = int(check(n*pc))
    top_n_indices = sorted_indices[:n].astype(int)  
    new_g = g[top_n_indices]  
    return new_g


def hybrid_mutation(g):
    history = numpy.copy(g)  
    for i in range(0, n, 2): 
        num_rand = random.randint(1, bits_num - 1)  
        temp = g[i][:num_rand].copy()  
        g[i][:num_rand] = g[i + 1][:num_rand].copy()  
        g[i + 1][:num_rand] = temp  
    after = g
    mutation_coefficient = (n * bits_num * pm) # Hệ số đột biến
    print(f"Ta co: {n} x {bits_num} x {pm} = {mutation_coefficient} bit")
    num_pos = random.sample(range(6),int(mutation_coefficient))
    for i in range(int(mutation_coefficient)):
        if g[0][num_pos[i]]  == 1:
            g[0][num_pos[i]] = 0
        else:
            g[0][num_pos[i]] = 1
        

    df = pandas.DataFrame({
        "Ca the" : range(n),
        "Truoc lai ghep": [''.join(str(int(bit)) for bit in chromosome) for chromosome in history],
        "Sau lai ghep" : [''.join(str(int(bit)) for bit in chromosome) for chromosome in after],
        "The he sau": [''.join(str(int(bit)) for bit in chromosome) for chromosome in g],
    })
    df = df.set_index("Ca the")
    print(df)
    return g

def show_answer(g):
    encoded_x,encoded_y,func,p,s,num = get_value(g)
    df = pandas.DataFrame({
        'Ca the': range(n),
        'Chuoi NST': [''.join(str(int(bit)) for bit in chromosome) for chromosome in g],
        'Ma hoa X': encoded_x,
        'Ma hoa Y': encoded_y,
        'f': func,
        'p': p,
        's': s,
        'n': num
    })
    df = df.set_index('Ca the')
    print(df)


show_answer(g)
print("___________________________________New Population__________________________________")
new_g = new_population(g)
show_answer(new_g)
print("___________________________________Hybrid And Mutation______________________________")
hybrid_mutation(new_g)
