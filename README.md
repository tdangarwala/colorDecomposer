# colorDecomposer
A project to figure out the recipe of base colors needed to create a color in the real world. The base colors in this case will include commonly found artist paints such as titanium white, carbon black, burnt sienna, etc.

This program uses the PyQt library to create a user interface to allow the user to either select colors and ratios to mix or upload an image and select a color to decompose.

The current decomposition process is as follows (once user selects region on input image to analyze):
1. Average rgb of selected region generated (target)
2. Reflectance of base colors (titanium white, carbon black, cadmium yellow, etc) estimated using Gaussian Distribution across a variety of wavelengths
3. Reflectance of target color estimated using the same as 2
4. K/S (scattering/absorptivity) values of target and base colors calculated using the reflectances
5. A regularization parameter is introducted to address how bright the color is as that impacts mixing ratios as well
6. A system of equations is solved for using ElasticNet to compute amount of each color. ElasticNet is useful because it helps ensure that the output is sparse (dont have a bunch of colors showing up in small percentages) and if 2 colors have similar behavior it picks one. 


Disclaimer: The output is not correct at all and the main reason I've found is that the gaussian distribution does not fully capture the nuances of the reflectance spectrum of each color. A better option would be to use a spectrophotometer but I dont have that. I've learned about PyQt, regression and regularization techniques, and a bit about color theory.

The functionality I'm trying to match is that of this website: 
https://goldenartistcolors.com/mixer/oil?tab=match-color
https://goldenartistcolors.com/mixer/acrylic

The match tab is exactly what I'm trying to build. Hopefully I can come close!
