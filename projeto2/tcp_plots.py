from scapy.all import rdpcap, IP, TCP
import matplotlib.pyplot as plt


tcp_packets = rdpcap('tcp-capture-artur.pcapng')


for pkt in tcp_packets:
    if len(pkt[TCP].payload) > 0:
        client_ip = pkt[IP].src
        sever_ip = pkt[IP].dst
        break

t0 = tcp_packets[0].time

# grafico 1
packet_times = []
seq_numbers = []



initial_seq = None

for pkt in tcp_packets:
    current_time = pkt.time - t0
    payload_size = len(pkt[TCP].payload)
    
    if pkt[IP].src == client_ip:
        if initial_seq is None:
            initial_seq = pkt[TCP].seq
        
        rel_seq = pkt[TCP].seq - initial_seq
        packet_times.append(current_time)
        seq_numbers.append(rel_seq)

seq_numbers_kb = [s / 1024 for s in seq_numbers]

plt.figure(figsize=(9, 5))

# Desenha a linha em degraus (horizontal até o próximo tempo, depois sobe na vertical)
plt.step(
    packet_times, 
    seq_numbers_kb, 
    where="post", 
    color="#301934", 
    linewidth=1.2, 
    label="Trajetória TCP (Stevens)"
)

# Desenha os pontos por cima da linha (os mesmos pontos do Wireshark)
plt.scatter(
    packet_times, 
    seq_numbers_kb, 
    color="#301934", 
    s=12, 
    zorder=3
)

plt.title("Gráfico 1: Número de Sequência vs Tempo")
plt.xlabel("Tempo (s)")
plt.ylabel("Número de Sequência (kB)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig("grafico1.png", dpi=300)


# grafico 2
waiting_for_ack = {}

sample_rtt_list = [] 
rtt_timestamp = []


for pkt in tcp_packets:
    current_time = pkt.time - t0
    payload_size = len(pkt[TCP].payload)
    
    print(pkt[TCP].flags)
    # pacote com dados enviado pelo cliente
    if (pkt[IP].src == client_ip) and (payload_size > 0):
        estim_time = pkt[TCP].seq + payload_size
        # se mandar o mesmo >1 vez, considerar o primeiro só
        if estim_time not in waiting_for_ack:
            waiting_for_ack[estim_time] = current_time
    
    # Ack enviado pelo servidor
    elif (pkt[IP].dst == client_ip) and ("A" in pkt[TCP].flags):
        accumulated_ack = pkt[TCP].ack
        
        acked = [estim_time for estim_time in waiting_for_ack if accumulated_ack >= estim_time]
        
        for min_ack_time in acked:
            sent_time = waiting_for_ack[min_ack_time]
            sample_rtt = current_time - sent_time
            
            sample_rtt_list.append(sample_rtt)
            rtt_timestamp.append(current_time)
            waiting_for_ack.pop(min_ack_time)

alpha = 0.125
estimated_rtt_list = []
curr_est= None
for sample in sample_rtt_list:
    if curr_est is None:
        # Primeiro
        curr_est = sample
    else:
        curr_est = (1 - alpha) * curr_est + (alpha * sample)
    
    estimated_rtt_list.append(curr_est)

estimated_rtt_ms = [1000*t for t in estimated_rtt_list]
sample_rtt_ms = [1000*t for t in sample_rtt_list]


# plotta
plt.figure(figsize=(9, 5)) 
plt.scatter(
    rtt_timestamp, 
    sample_rtt_ms, 
    color="royalblue", 
    alpha=0.6, 
    s=25, 
    label="SampleRTT (por segmento)"
)

# Curva contínua sobreposta (EstimatedRTT)
plt.plot(
    rtt_timestamp, 
    estimated_rtt_ms, 
    color="crimson", 
    linewidth=2.2, 
    label=r"EstimatedRTT ($\alpha = 0{,}125$)"
)

plt.title("Gráfico 2: RTT por Segmento e Curva de EstimatedRTT vs. Tempo")
plt.xlabel("Tempo decorrido (s)")
plt.ylabel("RTT (ms)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()

# Guarda o ficheiro e mostra no ecrã
plt.savefig("grafico2_rtt.png", dpi=300)

# grafico 3
throughputs = []
throughput_times = []

interval_time = 0.07
num_intervals = int(2.7 / interval_time) # 2.7, pois o experimento durou uns 2.7 segundos
bytes_per_interval = [0] * num_intervals


for pkt in tcp_packets:
    current_time = pkt.time - t0
    payload_size = len(pkt[TCP].payload)
    
    if pkt[IP].src == client_ip:
        interval_index = int(current_time // interval_time)

        bytes_per_interval[interval_index] += payload_size

for bytes in bytes_per_interval:
    throughputs.append(bytes/interval_time) # vazão desse intervalo de tempo

for i in range(len(throughputs)):
    throughput_times.append(i * interval_time + interval_time / 2)

throughputs_kb = [t / 1024 for t in throughputs]

plt.figure(figsize=(9, 5))

# Plota em barras usando a largura exata da sua janela (interval_time)
plt.bar(
    throughput_times, 
    throughputs_kb, 
    width=interval_time * 0.85,  # 0.85 deixa um pequeno espaço visual entre as colunas
    color="forestgreen", 
    alpha=0.8, 
    edgecolor="darkgreen",
    label="Vazão do intervalo"
)

plt.title("Gráfico 3: Vazão por Intervalo de Tempo")
plt.xlabel("Tempo decorrido (s)")
plt.ylabel("Vazão (kB/s)")
plt.grid(axis="y", linestyle="--", alpha=0.5    )
plt.legend()
plt.tight_layout()

plt.savefig("grafico3.png", dpi=300)