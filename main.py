import pygame, random, math, time, json


car_amount = 200
save_file = 'best_cars_trained.json'
with open('saved_data/'+save_file, 'r') as f:
        best_cars = json.load(f)
if len(best_cars['cars']) < car_amount:
    best_cars = best_cars['cars']
else:
    best_cars = best_cars['cars']
    best_cars = sorted(best_cars, key=lambda sort_car: sort_car[1])
    best_cars = best_cars[-car_amount:]


current_milli_time = lambda: int(round(time.time() * 1000))


average = lambda x, y: (x+y)/2

pygame.init()

screen = pygame.display.set_mode((1000,550))
width, height = pygame.display.get_surface().get_size()
clock = pygame.time.Clock()

pygame.display.set_caption('Car Learning')


colors = {
    "WHITE": (255, 255, 255),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "BLACK": (0, 0, 0),
    "GREY": (64, 64, 64),
    "YELLOW": (255, 255, 51),
    "ORANGE": (204,102,0),
}
generation = 0


def generate_best_cars(best_cars, cars):
    print('Best Cars')
    for c in best_cars:
        cars.append(car(c[0], c[2]))
    return cars

def kill_bad_cars(dead_cars, keep_percent=0.5):
    total_score = 0

    for car in dead_cars:
        total_score += int(car[1])

    keep_count = int(len(dead_cars)*keep_percent)

    for i in range(keep_count):
        random_point = random.randint(0, total_score)

        for i, c in enumerate(dead_cars):

            try:
                if c[1] < random_point < dead_cars[i+1][1] :
                    dead_cars.remove(c)

            except IndexError:
                if random_point > c[1]:
                    dead_cars.remove(c)

    return dead_cars


def generate_new_cars(dead_cars, car_amount, cars, mutation_rate = 0.05):

    for i in range(car_amount):
        car1 = random.choice(dead_cars)[0]
        car2 = random.choice(dead_cars)[0]
        gene = {}


        for i, d in enumerate(['up', 'down', 'left', 'right']):
            d_genes = []
            for g, i in enumerate(car1.genes[d]):
                avg_x = average(car1.genes[d][g][0], car2.genes[d][g][0])
                avg_y = average(car1.genes[d][g][1], car2.genes[d][g][1])

                if random.random() <= mutation_rate:
                    if random.choice([1, 2]) == 1:
                        avg_x = random.uniform(-1.5,1.5)
                    else:
                        avg_y = random.uniform(-1.5, 1.5)

                d_genes.append((avg_x, avg_y))

            gene[d] = d_genes
        color1 = car1.color
        color2 = car2.color
        color = ()
        for i, c in enumerate(color1):
            color += (int(average(c, color2[i])), )
        cars.append(car(gene, color))
    #dead_cars = []
    return cars, dead_cars

def generate_first_cars(car_amount, best_cars, cars):
    for c in best_cars:
        cars.append(car(c[0], c[2]))

    while len(cars) < car_amount:
        cars.append(car(None, None, newcar=True))

    return cars


class car:

    def __init__(self, genes, color, newcar=False):
        self.rect = pygame.Rect(50, 82.5, 30, 30)
        self.sensors = [
            [(20, 0), (40, 0), (60, 0), (80, 0), (100, 0),(100, 0)],
            [(15, -10), (30, -20), (45, -30), (60, -40), (75, -50)],
            [(15, 10), (30, 20), (45, 30), (60, 40), (75, 50)],
        ]

        if newcar:
            self.create_genes()
            self.color = (random.randint(0,250),random.randint(0,250),random.randint(0,250))

        else:
            self.genes = genes
            self.color = color

        self.is_moving = True
        self.movement_x = 0.5
        self.movement_y = 0
        self.score = 0
        self.crashed = False
        self.lastpos = self.rect.center
        self.poscount = 0


    def create_genes(self):
        self.genes = {}

        for i, d in enumerate(['up', 'down', 'left', 'right']):
            d_genes = []
            for direction in self.sensors:
                dir_genes = []
                for sensor in direction:
                     dir_genes.append((random.uniform(-2.5,2.5), random.uniform(-2.5,2.5)))
                d_genes = dir_genes
            self.genes[d] = (d_genes)


    def update(self, borders):
        if self.rect.collidelist(borders) != -1:
            self.crashed = True

        if not self.crashed:
            self.rect = self.rect.move(2*self.movement_x, 2*self.movement_y)

            self.score += math.sqrt(self.movement_x**2+self.movement_y**2)

            for i, sensor_list in enumerate(self.sensors):
                for index, sensor in enumerate(sensor_list):
                    s_rect_right = pygame.Rect(self.rect.center[0]+sensor[0]-5, self.rect.center[1]+sensor[1]-5, 10, 10)
                    s_rect_down = pygame.Rect(self.rect.center[0] + sensor[1] - 5, self.rect.center[1] + sensor[0] - 5, 10,10)
                    s_rect_left = pygame.Rect(self.rect.center[0] + -sensor[0] - 5, self.rect.center[1] + sensor[1] - 5, 10, 10)
                    s_rect_up = pygame.Rect(self.rect.center[0] + sensor[1] - 5, self.rect.center[1] + -sensor[0] - 5, 10, 10)

                    s_directions = [(s_rect_right, 'right'),(s_rect_down, 'down'),(s_rect_left, 'left'),(s_rect_up, 'up')]

                    for i, d in enumerate(s_directions):
                        if d[0].collidelist(borders) != -1:
                            # pygame.draw.rect(screen, colors["RED"],d[0])
                            self.movement_x = average(self.genes[d[1]][i][0], self.movement_x)
                            self.movement_y = average(self.genes[d[1]][i][1], self.movement_y)

                        # else:
                        #     pygame.draw.rect(screen, colors["BLUE"], d[0])





borders_coords = [(10, 10, 150, 5),(10, 50, 100, 5),(10, 10, 5, 40),
                  (160, 10, 5, 100),(110, 50, 5, 100),(110, 150, 150, 5),(160, 110, 100, 5)]

borders = []
for b in borders_coords:
    borders.append(pygame.Rect(3*b[0],3*b[1],3*b[2],3*b[3]))

cars = []
dead_cars = []

cars = generate_first_cars(car_amount, best_cars, cars)
# while len(cars) < car_amount:
#     cars.append(car(None, newcar=True))

gtime = pygame.time.get_ticks()

while True:

    screen.fill(colors["WHITE"])

    for b in borders:
        pygame.draw.rect(screen, colors['GREEN'], b)

    for c in cars:
        c.update(borders)
        if not c.crashed:
            if c.lastpos == c.rect.center:
                c.poscount += 1
                if c.poscount > 70:
                    c.crashed = True
                    c.is_moving = False
                    if c not in dead_cars:
                        dead_cars.append((c, c.score))
                    if c in cars:
                        cars.remove(c)
            else:
                c.poscount = 0
            c.lastpos = c.rect.center
            pygame.draw.circle(screen, c.color, c.rect.center, 15)

            if current_milli_time() - gtime > 3000 and c.rect.center[0] < 150:
                c.crashed = True
                c.is_moving = False
                if c not in dead_cars:
                    dead_cars.append((c, c.score))
                if c in cars:
                    cars.remove(c)

        else:
            c.crashed = True
            c.is_moving = False
            dead_cars.append((c, c.score))
            cars.remove(c)


    if gtime+15000 < current_milli_time():
        for c in cars:
            dead_cars.append((c, c.score))
        cars = []

    if len(cars) == 0:
        generation += 1
        print('Generation: '+str(generation))

        dead_cars = sorted(dead_cars, key=lambda sort_car: sort_car[1])
        best_cars.append((dead_cars[-1][0].genes,dead_cars[-1][1],dead_cars[-1][0].color))
        best_cars = sorted(best_cars, key=lambda sort_car: sort_car[1])
        print("Top Score: " + str(round(dead_cars[-1][1], 2)) + " -- All Time: " +str(round(best_cars[-1][1],2)))
        best_cars = best_cars[-car_amount:]
        if generation % car_amount == 0:
            cars = generate_best_cars(best_cars, cars)
        else:
            dead_cars = kill_bad_cars(dead_cars)
            dead_cars = sorted(dead_cars, key=lambda sort_car: sort_car[1])
            cars, dead_cars = generate_new_cars(dead_cars, car_amount, cars)

        if generation % 10 == 0:
            with open('saved_data/'+save_file, 'w') as f:
                json.dump(best_cars, f)

        gtime = current_milli_time()




    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            best_cars = {'cars':best_cars[-car_amount:]}
            with open('saved_data/'+save_file, 'w') as f:
                json.dump(best_cars, f)
            quit()




