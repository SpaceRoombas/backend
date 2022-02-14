import network.server_gateway

gateway = network.server_gateway.ServerGateway()

# Import guard
if __name__ == "__main__":
    gateway.start(9001)