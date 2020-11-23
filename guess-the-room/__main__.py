from . import train, get_room_data, k_nearest_neighbor

train()
input = get_room_data()
output = k_nearest_neighbor(11, input)

print(
    f"You're in the {output[0]} with probability {round(output[1] * 100, 2)}"
)
