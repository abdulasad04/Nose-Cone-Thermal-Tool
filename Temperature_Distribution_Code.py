import numpy as np
import copy
from matplotlib import pyplot as plt
# NOTE!!!! This code must run with a textfile that includes the time in sec, temperature of the air in celcius, and speed of the rocket in m/s. In that order, yo ucan download the data from an openrocket simulation

# Initial temperature of rocket in celcius
T_init = 15
#Time till motor burnout in s
t = 6

#Change parameters based on different nose cones
#________________________________________________
#The length of the nose cone in meters
length = 0.563
# radius of the tip of the nose cone measured in meters. The thickness of the nose cone is 2cm therefore that should be
# the min tip radius
radius_nc_tip = 0.002
# Material/thermal conductivity in W/m K
conduc = 0.04
# Specific heat capacity in J/Kg * K
heatcapac = 700
# Density of material in Kg/m^3
rho = 1850
# emissivity of material
emissivity = 0.75


def get_flux_heat(radius_nc_tip, v):
    '''Returns the heat flux in W/m^2 given radius of nose cone at tip in m and velocity v in m/s'''
    N = 0.5
    M = 3
    # air density at 20 degrees celcius in Kg/m^3
    air_density = 1.2
    # Formula: 1.83*10^-8/r_tip^0.5 * (1-gw)
    # Assume gw (ratio of cone enthalpy and air enthalpy) is 0 for worst case scenerio
    C = 1.83*10**-8/(radius_nc_tip**0.5)
    return C * air_density**N*v**M

def heat_solver(kappa, emiss, L, T_init, heat_flux, conduc):
    '''Solves for the temperature distribution of the cone at a certain time interval given the emissivity, diffusivity, length, initial temperature, conductivity, and heat flux of the nose cone'''
    steph_boltz_const = 5.67*10**-8
    file = open("openrocket_values.txt")
    line=file.readline()
    air_temp = []
    while line:
        air_temp.append(float(line[2]))
        line = file.readline()
    #Based on values given in txt file
    time_steps = 158
    burnout_time = 6
    dt = burnout_time/time_steps
    # Position on nose cone
    pos = np.linspace(0, L, time_steps)
    delta_p = pos[1] - pos[0]
    # initializing time and temperature
    t = np.linspace(0, burnout_time, int(burnout_time/dt))
    temperature = np.full((1, len(pos)), T_init)
    #Storing temperature
    temp_store=[]
    temp_store.append((copy.deepcopy(temperature)))
    # Iterative solver
    for idx in range(len(t)):
        # Reseting the temperature
        Tnew=np.zeros((1, time_steps))
        #Re-calculating the temperature distribution across the nose cone
        # Equation:  Tn+1 = k*t(Tx+1-2Tx+Tx-1)/[x]^2+Tn
        for idx2 in range(1, time_steps-1):
            Tnew[0][idx2] = temperature[0][idx2-1] + kappa*(dt/delta_p**2)*(temperature[0][idx2+1]-2*temperature[0][idx2]+temperature[0][idx2-1])
        #boundary conditions
        # Equation: Tx = -x/k(qx + (T^4-Tair^4))+Tx+1
        Tnew[0][0] = Tnew[0][1] - (delta_p/conduc) * (-heat_flux[idx] + emiss*steph_boltz_const*(temperature[0][0]**4 - air_temp[idx]**4))
        # Tl = Tl-1
        Tnew[0][time_steps-1] = Tnew[0][time_steps-2]
        # Changing temperature and storing
        temperature = copy.deepcopy(Tnew)
        temp_store.append(copy.deepcopy(temperature))
    return pos, t, temp_store

def get_flux_heat_with_HWC(radius_nc_tip, v, temperature, pos):
    '''Returns the heat flux with the correction factor included in W/m^2 given radius of nose cone at tip in m, temperature of the nose cone in degrees celcius and position along the nose cone in meters and velocity v in m/s'''
    N = 0.5
    M = 3
    # air density at 20 degrees celcius in Kg/m^3
    air_density = 1.2
    # Formula: 1.83*10^-8/r_tip^0.5
    C = 1.83*10**-8/(radius_nc_tip**0.5)

    #Calculating hw and hinf
    #Specific heat capcity of ait in J/kg K
    specific_heat_air = 1000
    #Calculating integral of Cp times temp
    integ=0
    for idx in range(len(temperature)-1):
        integ += specific_heat_air*(temperature[idx]+temperature[idx+1])/2 *(pos[idx+1]-pos[idx])
    # correction factor
    gw = integ/(integ+0.5*v**2)
    #Equation: C*rho^N*c^M*(1-hw/hinf)
    return C * air_density**N*v**M*(1-gw)

def thermal_tool(radius_nc_tip, length, T_init, diffusivity, emiss, conduc):
    '''Takes in the radius of the tip of the nose cone, the length, the initial temperature, the diffusivity, the emissivity, and the conductivity of the nose cone and returns the temperature profile'''
    simulation_values = open("openrocket_values.txt")
    line = simulation_values.readline()
    time = []
    heat_flux = []
    while line:
        line = line.split()
        # Getting the speed from the textfile and using it to calculate the heat flux at that point in time
        heat_flux.append(get_flux_heat(radius_nc_tip, float(line[2])))
        # Gets the time to plot heat flux versus time
        time.append(float(line[0]))
        line = simulation_values.readline()

    #Calculating initial temperature estimate
    x, t, Tstr = heat_solver(diffusivity, emiss, length, T_init, heat_flux, conduc)


    # Iterative solver
    #Change this based on how accurate you want the temperature distribution to be (Larger numbers are more accurate but take more time)
    n = 3
    for i in range(n):
        #Recalculating heat flux with correction factor based on temperature
        simulation_values = open("openrocket_values.txt")
        line = simulation_values.readline()
        heat_flux = []
        idx = 0

        while line:
            line = line.split()
            heat_flux.append(get_flux_heat_with_HWC(radius_nc_tip, float(line[2]), Tstr[0][idx], x))
            line = simulation_values.readline()
        #Recalculating heat flux based on new temperature
        x, t, Tstr = heat_solver(diffusivity, emiss, length, T_init, heat_flux, conduc)

    plt.plot(time, heat_flux)
    # plotting heat flux with respect to time
    plt.title("heat flux with respect to time")
    plt.xlabel("Time (s)")
    plt.ylabel("heat flux (W/m^2)")
    plt.show()
    # plotting heat distribution across the length of the nose cone
    plt.plot(x, np.transpose(Tstr[-1]))
    plt.title("heat distibution across nose cone")
    plt.xlabel("Length (m)")
    plt.ylabel("Temperature (Celcius)")
    plt.show()
    print("Max Temp: ", Tstr[-1][0][0], "Celcius")


thermal_tool(radius_nc_tip, length, T_init, conduc/(heatcapac*rho), emissivity, conduc)
