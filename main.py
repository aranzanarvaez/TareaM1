import mesa
import matplotlib.pyplot as plt
import numpy as np



def compute_gini(model):
    agent_wealths = [agent.puntos for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B

def sumPoint(model)->int:
    s = [agent.puntos for agent in model.schedule.agents]
    y = sum(s)
    return y

class AspiradoraAgent(mesa.Agent):
    """An agent with fixed initial wealth."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.puntos = 1

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def clean(self):
        
        celda = self.model.grid.get_cell_list_contents([self.pos])
        for element in celda:
            if isinstance(element, TrashAgent) == True:
                self.model.grid.remove_agent(element)
                self.puntos += 1
            

    def step(self):
        self.move()
        self.clean()


class AspiradoraModel(mesa.Model):
    """A model with some number of agents."""   
    def __init__(self, N, Basura, width, height):
        self.num_agents = N
        self.basura = Basura
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.schedule2 = mesa.time.RandomActivation(self)
        self.running = True
        
        for i in range(self.num_agents):
            a = AspiradoraAgent(i, self)
            self.schedule.add(a)
            self.grid.place_agent(a, (0, 0))

        for i in range(self.basura):
            a = TrashAgent(i + self.num_agents, Basura)
            self.schedule2.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": compute_gini}, agent_reporters={"Wealth": "puntos"}
            
        )
        
    
   
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        suma = sumPoint(self)
        if (suma == 25):
            self.running = False



        

        


class TrashAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        


model = AspiradoraModel(5, 20, 10, 10)
for i in range(100):
    model.step()
   

params = {"width": 10,  "height": 10, "N": 5,"Basura": 20}

results = mesa.batch_run(
    AspiradoraModel,
    parameters=params,
    iterations=5,
    max_steps=50,
    number_processes=1,
    data_collection_period=1,
    display_progress=True,
)

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                "Filled": "true",
                "r": 0.5}

    if agent.unique_id < 5:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.3
    return portrayal

grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 500, 500)

chart = mesa.visualization.ChartModule([{"Label": "Gini",
                      "Color": "Black"}],
                    data_collector_name='datacollector')

server = mesa.visualization.ModularServer(AspiradoraModel,
                       [grid, chart],
                       "Aspiradora Model",
                       {"N":5, "Basura":20,"width":10, "height":10})


server.port = 8521  # The default
server.launch()


