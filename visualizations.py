import os
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

nbuddies_path = os.path.dirname(os.path.realpath(__file__))

def movie_3D(tail_length : int = 10):
    """
    Loads data and makes movie of motion in 3D space with tails behind them

    Parameters
    ----------
    tail_length : int, default 10
        length of tail trailing behind points
    """
    
    #set up
    if not os.path.exists(nbuddies_path+"/movie_dump"):
        os.makedirs(nbuddies_path+"/movie_dump")
    
    #getting info from sim end
    last_batch_num = _find_last_batch_num()
    with open(nbuddies_path + f"/data/data_batch{last_batch_num}.pkl", 'rb') as file:
        data = pickle.load(file)[0]
    N = len(data)
    max_range = 0
    for n in range(N):
        if np.linalg.norm(data[n].position) > max_range:
            max_range = np.linalg.norm(data[n].position)
    max_range *= 2 # add buffer

    #getting info from sim start
    with open(nbuddies_path + f"/data/data_batch0.pkl", 'rb') as file:
        init_data = pickle.load(file)[0]
    plotting_data = np.zeros([N, 3, tail_length])
    for n in range(N):
        for t in range(tail_length):
            plotting_data[n, :, t] = init_data[n].position
    
    #generating movie frames
    for i in range(last_batch_num + 1):
        
        #slide data window forward
        for j in range(tail_length - 1):
            plotting_data[:,:,j] = plotting_data[:,:,j+1]
        with open(nbuddies_path + f"/data/data_batch{i}.pkl", 'rb') as file:
            data = pickle.load(file)[0]
        for n in range(N):
            plotting_data[n, :, -1] = data[n].position

        #plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for n in range(N):
            #plotting tails
            for t in range(tail_length - 1):
                alpha = t / (tail_length - 2)
                ax.plot(plotting_data[n,0,t:t+2], plotting_data[n,1,t:t+2], plotting_data[n,2,t:t+2], 'b-', alpha=alpha)

            #plotting points
            ax.scatter(plotting_data[n,0,-1], plotting_data[n,1,-1], plotting_data[n,2,-1], c="black", s=100, marker="o")

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Black Hole Trajectories')

        ax.set_xlim( - max_range/2, max_range/2)
        ax.set_ylim( - max_range/2, max_range/2)
        ax.set_zlim( - max_range/2, max_range/2)
        
        plt.tight_layout()
        plt.savefig(nbuddies_path + f"/movie_dump/trajectories_{i}.png", dpi=300, bbox_inches='tight')
        plt.close()

    _recompile_movie_3D()

def _recompile_movie_3D():
    """
    Deletes movie if it exists then recreates it by compiling the pngs in movie_dump
    """
    if os.path.exists(nbuddies_path+"/trajectories.mkv"):
        os.remove(nbuddies_path+"/trajectories.mkv")
    os.system("ffmpeg -framerate 12 -start_number 0 -i "+nbuddies_path+"/movie_dump/trajectories_%01d.png -q:v 0 "+nbuddies_path+"/trajectories.mkv")


def _find_last_batch_num():
    """
    finds num of last batch file saved

    Returns
    -------
    int
        num of last batch file saved
    """
    i = 0
    while os.path.exists(nbuddies_path + f"/data/data_batch{i}.pkl"):
        i += 1
    return i - 1

movie_3D()