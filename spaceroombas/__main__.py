import network.server_gateway

gateway = network.server_gateway.ServerGateway()

if __name__ == "__main__":
    print("Welcome to the SpaceRoombas server!")
    gateway.start()