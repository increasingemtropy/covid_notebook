# covid_notebook
Importing, manipulating and plotting data for novel coronavirus data

This repository contains:
An R script that imports coronavrius data from John Hopkins University and plots the data since ~March until the current day.
 - The plot only features a subset of countries, and plots the cumulative cases over 14 days per 10k population. 
 - This allows us to make rough comparisons between different countries.

A python script that imports the same data and plots the same data range
 - The functions defined here import, clean and then streamline the data to relevant stats
 - Further, we can plot not only the raw data, but the growth rate of the virus based on these data
 
 Still TO DO:
* Put everything into functions that can be called from a master script
* Automate more of the graph settings (min, max, colours, ticks etc)

