from scapy.all import rdpcap, IP, UDP, DNS, TCP
import matplotlib.pyplot as plt
import numpy as np

udp_packets = rdpcap('udp-capture-artur.pcapng')
tcp_packets = rdpcap('tcp-capture-artur.pcapng')


for pkt in udp_packets:
    if len(pkt[UDP].payload) > 0:
        client_ip = pkt[IP].src
        sever_ip = pkt[IP].dst
        break

t0 = udp_packets[0].time

# grafico 1
rtt_time = []
rtt_instant = []
waiting_queries = {}

for pkt in udp_packets:
    current_time = pkt.time - t0
    id = pkt[DNS].id #udp n tem seq number
    
    # Cliente fazendo uma query
    if pkt[DNS].qr == 0:
        if id not in waiting_queries:
            waiting_queries[id] = current_time
    
    # Servidor respondendo
    elif pkt[DNS].qr == 1:
        if id in waiting_queries:
            sent_time = waiting_queries[id]
            rtt = current_time - sent_time
            
            rtt_time.append(rtt)
            rtt_instant.append(current_time)

            waiting_queries.pop(id)
            
            
plt.figure(figsize=(9, 5))
plt.scatter(rtt_instant, rtt_time, color="#b39eb5", s=30, label="DNS RTT")

plt.title("RTT das Consultas DNS (UDP)")
plt.xlabel("Tempo decorrido (s)")
plt.ylabel("RTT (ms)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig("dns_rtt.png", dpi=300)


# grafico 2
for p in tcp_packets:
    sample_tcp = p[TCP]

for p in udp_packets:
    sample_udp = p[UDP]
    
def get_size_fields(sample):
    field_sizes = {}
    

    # na documentação fields.Bitfield tem size e fields.Field tem sz, muito legal trabalhar com essa biblioteca (contém ironia)
    for f in sample.fields_desc:
        bits = getattr(f, "size", None)
        bytes = getattr(f, "sz", None)
        if bits:
            field_sizes[f.name] = bits
        elif bytes:
            field_sizes[f.name] = 8*bytes
        else: 
            #nunca cai aqui
            pass
            
    return field_sizes

tcp_fields = get_size_fields(sample_tcp)
print(tcp_fields)
udp_fields = get_size_fields(sample_udp)
print(udp_fields)


# pega os dados
both = [k for k in tcp_fields.keys() if k in udp_fields]
tcp_only = [k for k in tcp_fields if k not in both]
udp_only = [k for k in udp_fields if k not in both]

# escolhe as posições no grafico
gap = 1.2
pos_both = [float(i) for i in range(len(both))]

offset_udp = (pos_both[-1] if pos_both else -1) + 1 + gap
pos_udp = [offset_udp + i for i in range(len(udp_only))]

offset_tcp = (pos_udp[-1] if pos_udp else pos_both[-1]) + 1 + gap
pos_tcp = [offset_tcp + i for i in range(len(tcp_only))]

x_coords = pos_both + pos_udp + pos_tcp
x_labels = both + udp_only + tcp_only

y_udp = [tcp_fields.get(c, 0) for c in x_labels]
y_tcp = [udp_fields.get(c, 0) for c in x_labels]

largura = 0.5

fig, ax = plt.subplots(figsize=(13, 6))

bars_udp = ax.bar(
    [x - largura / 2 for x in x_coords],
    y_udp,
    width=largura,
    label="UDP",
    color="#b39eb5",
    edgecolor="black",
    linewidth=0.5,
)
bars_tcp = ax.bar(
    [x + largura / 2 for x in x_coords],
    y_tcp,
    width=largura,
    label="TCP",
    color="#127424",
    edgecolor="black",
    linewidth=0.5,
)

# 5. Adicionar divisórias verticais para delimitar as 3 regiões
div1 = pos_both[-1] + 1 + (gap / 2) - 0.5
div2 = pos_udp[-1] + 1 + (gap / 2) - 0.5

max_y = max(max(y_udp), max(y_tcp)) + 0.5
y_text = max_y + 4

# Rótulos textuais superiores para cada bloco
ax.text(
    sum(pos_both) / len(pos_both),
    y_text,
    "TCP & UDP",
    ha="center",
    fontweight="bold",
    fontsize=10,
    color="BLACK",
)
ax.text(
    sum(pos_udp) / len(pos_udp),
    y_text,
    "Apenas UDP",
    ha="center",
    fontweight="bold",
    fontsize=11,
    color="BLACK",
)
ax.text(
    sum(pos_tcp) / len(pos_tcp),
    y_text,
    "Apenas TCP",
    ha="center",
    fontweight="bold",
    fontsize=10,
    color="BLACK",
)

potencias_2 = [2, 4, 8, 16, 32]

# 2. Aplicar no eixo Y
ax.set_yticks(potencias_2)
ax.set_yticklabels([str(p) for p in potencias_2])
ax.set_ylim(0, 36)

# Configurações de eixos e legenda
ax.set_title(
    "Comparação Estrutural dos Cabeçalhos: UDP vs. TCP (em Bits)",
    fontsize=14,
    pad=20,
)
ax.set_ylabel("Tamanho (b)", fontsize=11)
ax.set_xticks(x_coords)
ax.set_xticklabels(x_labels, rotation=35, ha="right", fontsize=10)
ax.set_ylim(0, max_y + 7)
ax.grid(axis="y", linestyle=":", alpha=0.6)
ax.legend(loc="upper right")

plt.tight_layout()
plt.savefig("comparacao_campos_categorizados.png", dpi=300)

            

