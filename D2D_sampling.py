#importing libs 
import time 
import matplotlib.pyplot as plt
import random
from sklearn.cluster import KMeans

class Customer:
    def __init__(self, customer_number, x, y):
        self.customer_number = str(customer_number)
        self.x = float(x)
        self.y = float(y)
        
    def __str__(self):
        return "Customer number: " + self.customer_number
    
    def pair(self):
        return [self.x,self.y]


class Graph:
    global file_name
    def __init__(self, customer_list, tours = [], algo_name : str = None, kind_of_tour : str = None,tour_drone : list = None):
        self.file_name = file_name[0:-4]
        self.customer_list = customer_list
        self.algo_name = algo_name
        self.kind_of_tour = kind_of_tour
        self.tour_drone = tour_drone
        self.tours = tours 
        
    def draw_lines(self,tour,color):
        for n in range(len(tour)-1):
            point1 = [self.customer_list[tour[n]].x,self.customer_list[tour[n+1]].x]
            point2 = [self.customer_list[tour[n]].y,self.customer_list[tour[n+1]].y]
            plt.plot(point1, point2, color)
        
    def draw(self):
        plt.figure(figsize = (14,7))
        plt.scatter(self.customer_list[0].x, self.customer_list[0].y, color = "red")
        plt.scatter([item.x for item in self.customer_list[1:]], [item.y for item in self.customer_list[1:]], color = 'blue')

        for n in range(len(customer_list)):
            plt.annotate(str(n), xy=(self.customer_list[n].x, self.customer_list[n].y), xytext = (self.customer_list[n].x + 0.03, self.customer_list[n].y), color = 'black')
        matplotlib_colors = ["saddlebrown", "midnightblue","cadetblue","fuchsia"]
        
        if len(self.tours) != 0 and self.kind_of_tour is not None:
            if self.kind_of_tour == "Technician":
                colors = matplotlib_colors[:]
                for tour in self.tours:
                    color = colors[-1]
                    colors.pop()
                    self.draw_lines(tour,color)
            elif self.kind_of_tour == "Drone":
                self.tours.append(self.tour_drone[:])
                colors = matplotlib_colors[:]
                colors.append("green")
                for tour in self.tours[::-1]:
                    color = colors[-1]
                    colors.pop()
                    self.draw_lines(tour,color)
            
        plt.xlabel("X")
        plt.ylabel("Y")
        if self.algo_name is None: 
            plt.title("Graph of customer in {0} data set".format(self.file_name))
        else:
            plt.title("Graph for nodes in {0} data set using the {1} algorithm".format(self.file_name, self.algo_name))
        return plt.show()

def total_distance(tour, distances):
    distance = 0
    for n in range(len(tour)-1):
        distance += distances[(tour[n],tour[n+1])]
    return distance 

def nearest_neighbor(node_list, distances, starting_node=0):
    res = [starting_node]
    node_list_number = [int(customer.customer_number) for customer in node_list[1:]]
    while len(res) < len(node_list):
        i = res[-1]
        nn = {(i,j): distances[(i,j)] for j in node_list_number if j != i and j not in res}
        new_edge = min(nn.items(), key = lambda x: x[1])
        res.append(new_edge[0][1])
        
    res.append(starting_node)
    return res, total_distance(res, distances)

def algo_2opt(avail_tour, distances):
    for i in range(len(avail_tour) - 2):
        optimal_change = 0
        for j in range(i+2, len(avail_tour)-1):
            old_cost = distances[(avail_tour[i], avail_tour[i+1])] + distances[(avail_tour[j], avail_tour[j+1])]
            new_cost = distances[(avail_tour[i], avail_tour[j])] + distances[(avail_tour[i+1], avail_tour[j+1])]
            change = new_cost - old_cost
            
            if change < optimal_change: 
                optimal_change = change
                optimal_i, optimal_j = i, j
        
        #if we found an optimal swapped edges (just one optimal pair for each node i), then update the tour
        if optimal_change < 0:
            avail_tour[optimal_i+1:optimal_j+1] = avail_tour[optimal_i+1:optimal_j+1][::-1]
        
    return avail_tour, total_distance(avail_tour, distances)

time_tech_tour = lambda tour_distance: str(round(tour_distance/0.58, 2)) + " minutes"
time_drone_tour = lambda tour_distance: str(round(tour_distance/0.83, 2)) + " minutes"


if __name__ == "__main__":
    # file_name = input("Enter the name of the data set you want to use: ")
    # if file_name[-4:] != ".txt":
    #     file_name += ".txt"

    file_name = "20.5.1.txt"
        
    with open("data/" + file_name, 'r') as file:
        no_of_customer = int(file.readline().split()[-1])
        customer_list = []
        customer_list.append(Customer(0,0,0))
        file.readline()
        for customer in range(no_of_customer):
            x, y, demand = file.readline().split()
            customer_list.append(Customer(customer+1,x,y))

    #relation between customers
    customer_edges = [(i,j) for i in range(no_of_customer+1) for j in range(no_of_customer+1) if i != j]

    #distances between customers
    customer_distances = {(i,j):((customer_list[i].x-customer_list[j].x)**2 + (customer_list[i].y-customer_list[j].y)**2)**0.5 for i,j in customer_edges}

    #basic map, plot 1st
    # basic_map = Graph(customer_list)
    # basic_map.draw()

    ls_of_no_of_technician = [1,2,3,4]

    #make a file
    result_file = open("result.txt", "w+")  
    result_file.write("Current solution for the data set: {0} \n\n".format(str(file_name)))
    result_file.close()

    result_file = open("result.txt", "a+") 

    for no_of_technician in ls_of_no_of_technician:
        result_file.write("Try with the number of technician = {0}\n\n".format(no_of_technician))
        kmeans = KMeans(n_clusters = no_of_technician)
        kmeans.fit([customer.pair() for customer in customer_list[1:]])

        zipped = list(zip(range(1, len(customer_list[1:])+1), kmeans.labels_))
        unzipped = []
        for i in range(no_of_technician):
            unzipped.append([customer_list[element[0]] for element in zipped if element[1] == i])

        tours = []

        for i in range(no_of_technician):
            technician_team = unzipped[i]
            technician_team.insert(0 ,customer_list[0])
            tour_tech, tour_tech_distance = nearest_neighbor(technician_team, customer_distances)
            tour_tech, tour_tech_distance = algo_2opt(tour_tech, customer_distances)
            time_tech = time_tech_tour(tour_tech_distance)
            tours.append([i, tour_tech, tour_tech_distance, time_tech])
        
        time_max_tech_tour = max(float(ele[3].split()[0]) for ele in tours)

        for ele in tours:
            result_file.write("Time of tour: {0}\nTour of technician: {1}\nDistance of the tour: {2}\nTime taken to complete tour: {3}\n\n".format(ele[0]+1, ele[1], ele[2], ele[3]))
            for node in ele[1][:-1]:
                small_tour = ele[1][:ele[1].index(node)+1]
                distance_small_tour = total_distance(small_tour, customer_distances)
                time_tech_small_tour = time_tech_tour(distance_small_tour)
                result_file.write("Technician {0} ---> node {1} : {2}\n".format(ele[0]+1, node, time_tech_small_tour))
            result_file.write("\n")
        result_file.write("\nTime when the last technician come back to the lab: {0} minutes\n".format(time_max_tech_tour))
        result_file.write("###########################################\n\n")

        technician_graph = Graph(customer_list,  [ele[1] for ele in tours], "k-means and 2-opt", "Technician")
        technician_graph.draw()

    result_file.write("EOF")
    result_file.close()

