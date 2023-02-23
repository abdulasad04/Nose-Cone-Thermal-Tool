# Nose-Cone-Thermal-Tool
## How To Get The Code To Work
This is a tool to determine temperature distribution and heat flux along nose cone.
### Getting the File Setup
Before you do anything, make sure that the OpenRocket file of the rocket you are testing is in the same directory as the Python Code.
To do this:
1. Have an OpenRocket file ready with the correct dimensions and specifications of your rocket
2. Save the file in the same directory/folder as the code

Then you should see the following line of code on the 16th line:
```doc = orh.load_doc(os.path.join("Defiance_OR.ork"))```. Here just make sure to change the "Defiance_OR.ork" to whatever the name of your OpenRocket file is.

### Changing the Initial Parameters
You should also see this line of code: 
```
T_init = 15
t = 6
length = 0.563
radius_nc_tip = 0.002
conduc = 0.04
heatcapac = 700
rho = 1850
emissivity = 0.75
```
between lines 17 - 36 of your file. To get an idea of what values to put for each variable see the corresponding header.

#### T_init
This is the initial temperature of your rocket in degrees celcius. In this example 15 degrees celcius is used as that is room temperature. However, if you happen to know that the initial temperature of the rocket will be higher or lower than this value than you should change it according. Otherwise, you should probably keep it at room temperature.

#### t
This is the time it takes for the rocket to reach motor burnout in s. Motor bunrout when the nose cone of the rocket is at its maximum temperature, which is why we choose this point in time. YOu can find this value from OpenRocket if you run a simulation.

#### length
This is the length of the nose cone in meters. 

#### radius_nc_tip
This is the radius of the tip of the nose cone. This value varies depending on the type of nose cone, nose cones like blunted conic or blunted ogive's tangent have a high tip of the nose cone, whereas a Haack series has a very small one. Note that increasign the radius of your nose cone will increase the aerodynamic drag of your nose cone. The radius of your nose cone is the easiest value you can modify if your nose cone experiences a temperature that is too high. This value can be obtained by physically measuring the nose cone.

#### conduc
This is the conductivity of your nose cone. Based on what material you make your nose cone out of you can change this value. You can find the conductivity of different materials by googling them.

#### heatcapac
This is the specific heat capacity of the material of your nose cone. You can also just search this value up if you know what material you are making your nose cone out of.

#### rho 
This is the density of the material of your nose cone measured in Kg/m<sup>2</sup>. This can be found through OpenRocket if you have the material of your nose cone already specified. 

#### emissivity
This is the emissivity of your nose cone. Don't worry you do not need to know what it means. Just Google **Emissivty of** and then whatever material you are using.

### Picking a Number of Iterations
Finally, on line 122 you should see something like: ```n = 3```. This is simply the number of iterations you are doing for this solver. Just know that more is more accurate, but also takes more time. I recommend not to go overboard here. I found that the difference between n = 3 and n = 100 is very small, but play around with it as it could be different with your own parameters. 

## The Math Behind It
The follwoing heat transfer problem involves using the following equations:
1. ∂T/∂t = α∇<sup>2</sup>T
2. ∇T = (1/κ)(q + (T<sup>4</sup>-T<sub>air</sub><sup>4</sup>))
3. q = C(ρ)<sup>0.5</sup>(V)<sup>3</sup>(1 - h<sub>w</sub>/h<sub>∞</sub>)/(R<sub>N</sub><sup>0.5</sup>) 

For a better understanding on what each term means and what assumptions are made when calculating these questions see the corresponding sections below. It is important to note that all three equations assum a **1D Simplification** of the problem.

### ∂T/∂t = α∇<sup>2</sup>T
Expanding the gradient using a one dimensional heat transfer problem gives us: ∂T/∂t =α(∂<sup>2</sup>T/∂x<sup>2</sup>). Like the previous equation we can turn this into a boundry value problem and get the following equation:  T<sub>n+1,x</sub> = Δt(α)(T<sub>n,x+1</sub>-2T<sub>n,x</sub>+T<sub>n,x-1</sub>)/[Δx]<sup>2</sup>+T<sub>n,x</sub>. There are 7 new variables in this equation, which are:
1. T<sub>n+1,x</sub>: This is the temperature of the nose cone at an arbitrary point x at a time step one more than the one we know.
2. Δt: This is the time between the iterations
3. α: This is the diffusivity of the nose cone, which is the conductivity divided by the product of the specific heat capacity and the density. 
4. T<sub>n,x+1</sub>: This is the temperature of the nose cone at a point one more than 'x', which is an arbitrary point chosen previously. This temperature is at a time step 'n', which is a point in time where we know the temperature profile of the nose cone.
5. T<sub>n,x</sub>: This is the temperature of the nose cone at an arbitrary point x at a time step 'n' that was chosen previously and must be a point in time where we known the temperature distribution across the nose cone.
6. T<sub>n,x-1</sub>: This is the temperature of the nose cone at an arbitrary point one less than 'x' which was already chosen previously. This temperature is at a point in time 'n' where the temperature across the nose cone is already known.
7. Δx: This is the disance between 'x' and 'x+1' or 'x-1' and 'x'. 

This boundary value problem has the three boundary conditions:
1. T<sub>0,x</sub> = T_init: This means that before the rocket takes flight it has the intiial temperature that you set. This is why it should most likely be kept at room temperature since the rocket should not be heating up before flight.
2. T<sub>length</sub> = T<sub>length-1</sub>: This means that the temperature of the nose cone near the very end is very close/indistinguishable. This is a good estimate because if you see the temperature distribution across the nose cone it begins to level out as you move far enough away from the tip of the nose cone.
3. ∇T = (1/κ)(q + (T<sup>4</sup>-T<sub>air</sub><sup>4</sup>)): This is an equation to find the temperature of the tip of the nose cone at the next time step. To learn more about this equation see the section below.

### ∇T = (1/κ)(q + (T<sup>4</sup>-T<sub>air</sub><sup>4</sup>))
Expanding the gradient using a one dimensional heat transfer problem gives us: ∂T/∂x = (1/κ)(qx + (T<sup>4</sup>-T<sub>air</sub><sup>4</sup>)). By discretizing the domain and turning this into a difference equation we get the following equation: T<sub>x</sub> = -Δx(q<sub>x</sub> + (T<sup>4</sup>-T<sub>air</sub><sup>4</sup>))/κ + T<sub>x+1</sub>. This equation is used as a boundary condition to find the temperature at the tip of the nose cone for the first equation, which is why we solved for T<sub>x</sub> and not T<sub>x+1</sub>. The equation has 7 varaibles, which are:
1. T<sub>x+1</sub>: this is the temperature at the distance Δx away from a known temperature.
2. Δx: This is the distance we choose away from a known point on the nose cone to an unknown point.
3. q<sub>x</sub>: This is the heat flux, which is the amount of heat transferring through an area of the material per unit of time.
4. T: This is the temperature of the nose cone at that point on the previous time step.
5. T<sub>air</sub>: This is the temperature of the air surrounding the nose cone.
6. κ: This is the conductivity of the nose cone.
7. T<sub>x</sub>: This is the temperature of a known point on the nose cone.

### q = C(ρ)<sup>0.5</sup>(V)<sup>3</sup>(1 - h<sub>w</sub>/h<sub>∞</sub>)/(R<sub>N</sub><sup>0.5</sup>) 
For this equation most of the givens are actually from open rocket themselves, but before we can calculate the enthalpy ratio, h<sub>w</sub>/h<sub>∞</sub>, we need to know the temperature of the nose cone because h<sub>w</sub> is the enthalpy of the nose cone and h<sub>∞</sub> is the enthalpy of the immediate surroundings of the nose cone. However, we need to know heat flux to get the temperature of the nose cone. So what we do is assume the enthalpy ratio is very small intially, this is a good approximation for rockets going at hypersonic speed. This gives us the following equation: q<sub>x</sub> = C(ρ)<sup>0.5</sup>(V)<sup>3</sup>/(R<sub>N</sub><sup>0.5</sup>) where we have 5 variables:
1. q<sub>x</sub>: This is the heat flux, which is the amount of heat transferring through an area of the material per unit of time.
2. C: This is a constant equal to 1.83(10<sup>-8</sup>).
3. ρ: This is the density of the nose cone.
4. V: This is the velocity of the nose cone. This value is obtained from OpenRocket directly.
5. R<sub>N</sub>: This is the radius of the tip of the nose cone.

Here we have all the variables except for 'q', the heat flux, and so we can solve for the heat flux and then use that to find the temperature across the nose cone. We then use the temperature across the nose cone along with these equations: h<sub>w</sub> = ∫C<sub>p</sub>Tdt and h<sub>∞</sub> = ∫C<sub>p</sub>Tdt + 0.5V<sub>∞</sub><sup>2</sup>, to recalculate the heat flux more accurately. The following equations have 5 variables, which are:
1. h<sub>w</sub>: The enthalpy of the nose cone.
2. C<sub>p</sub>: This is the specific heat capacity of the nose cone. Not to be confused with the arbitrary constant 'C' mentioned above. 
3. T: This is the temperature across the nose cone.
4. h<sub>∞</sub>: This is the enthalpy of the air within close proximity of the nose cone.
5. V<sub>∞</sub>: This is the velocity of the nose cone.

We then use this more accurate calculation of the heat flux to calculate the temperature and then use the more accurate calculation of temperature to calculate the heat flux and so on. This process continues for as long as you specify based on what you input as your answer for 'n'.
