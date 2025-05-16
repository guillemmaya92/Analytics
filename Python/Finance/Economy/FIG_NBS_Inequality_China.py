# Libraries
# =====================================================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Get Data (NBS and WID)
# =====================================================
data = {
    "year": list(range(1980, 2024)),
    "urban_population": [
        19140, 20171, 21480, 22274, 24017, 25094, 26366, 27674, 28661, 29540, 30195, 31203, 32175,
        33173, 34169, 35174, 37304, 39449, 41608, 43748, 45906, 48064, 50212, 52376, 54283, 56212,
        58288, 60633, 62403, 64512, 66978, 69927, 72175, 74502, 76738, 79302, 81924, 84343, 86433,
        88426, 90220, 91425, 92071, 93267
    ],
    "rural_population": [
        79565, 79901, 80174, 80734, 80340, 80757, 81141, 81626, 82365, 83164, 84138, 84620, 84996,
        85344, 85681, 85947, 85085, 84177, 83153, 82038, 80837, 79563, 78241, 76851, 75705, 74544,
        73160, 71496, 70399, 68938, 67113, 64989, 63747, 62224, 60908, 59024, 57308, 55668, 54108,
        52582, 50992, 49835, 49104, 47700
    ],
    "urban_consumption": [
        490, 517, 504, 547, 621, 750, 847, 953, 1200, 1345, 1404, 1623, 2017, 2676, 3671, 4810,
        5437, 5705, 5977, 6429, 7083, 7409, 7826, 8166, 8942, 9900, 10820, 12582, 14147, 15161,
        17119, 19853, 21563, 23386, 25264, 27039, 29324, 31454, 33700, 35841, 34823, 39205, 40066,
        43797
    ],
    "rural_consumption": [
        178, 202, 227, 252, 280, 346, 385, 427, 506, 588, 627, 661, 701, 822, 1073, 1344, 1655, 1768,
        1778, 1793, 1917, 2032, 2157, 2292, 2521, 2784, 3066, 3538, 3981, 4295, 4782, 5880, 6573,
        7397, 8365, 9409, 10609, 12145, 13985, 15460, 16209, 18720, 19929, 21953
    ],
    "gini_pre": [
        0.38, 0.39, 0.39, 0.39, 0.4, 0.4, 0.42, 0.42, 0.43, 0.44, 0.43, 0.45, 0.46, 0.48, 0.48,
        0.48, 0.47, 0.47, 0.47, 0.48, 0.5, 0.51, 0.53, 0.54, 0.55, 0.56, 0.56, 0.56, 0.56, 0.56,
        0.57, 0.56, 0.55, 0.56, 0.55, 0.56, 0.55, 0.56, 0.56, 0.56, 0.56, 0.57, 0.57, 0.57
    ],
    "gini_pos": [
        0.37678, 0.38164, 0.38878, 0.38653, 0.39165, 0.39926, 0.41379, 0.41783, 0.42156, 0.43046,
        0.4264, 0.44225, 0.45711, 0.47219, 0.47823, 0.47116, 0.46628, 0.46659, 0.46798, 0.4751,
        0.49029, 0.49467, 0.52002, 0.52932, 0.53136, 0.54142, 0.53733, 0.53991, 0.53665, 0.53439,
        0.53852, 0.53215, 0.51823, 0.5256, 0.51737, 0.51879, 0.51648, 0.52329, 0.51837, 0.5174,
        0.52289, 0.52394, 0.52394, 0.52394
    ],
   "gini_urb": [
        0.2415, 0.243, 0.2424, 0.2463, 0.2606, 0.2886, 0.2711, 0.2576, 0.267, 0.2738,
        0.2709, 0.2643, 0.2848, 0.3021, 0.3103, 0.3074, 0.3151, 0.3239, 0.3316, 0.3372,
        0.3456, 0.3589, 0.4127, 0.4245, 0.4383, 0.4464, 0.4492, 0.452, 0.456, 0.4516,
        0.4569, 0.4802, 0.4412, 0.474, 0.4466, 0.4474,
        None, None, None, None, None, None, None, None
    ],
    "gini_rur": [
        0.3329, 0.3422, 0.349, 0.3542, 0.3584, 0.3619, 0.3707, 0.3774, 0.3827, 0.387,
        0.3907, 0.4043, 0.4128, 0.4201, 0.4262, 0.4275, 0.43, 0.4315, 0.4267, 0.4311,
        0.4531, 0.4608, 0.4665, 0.4677, 0.4601, 0.4886, 0.483, 0.4921, 0.4903, 0.4963,
        0.5239, 0.5292, 0.5259, 0.524, 0.5232, 0.524, 
        None, None, None, None, None, None, None, None
    ]
}

df = pd.DataFrame(data)
df['var_consumption'] = df['urban_consumption'] / df['rural_consumption']
df['var_population'] = df['urban_population'] / df['rural_population']
df['gini'] = df['gini_pos']
df = df[['year', 'gini', 'var_consumption', 'var_population', 'gini_urb', 'gini_rur']]

# Data Visualization
# =====================================================
# Font and style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Franklin Gothic'], 'font.size': 9})
sns.set(style="white", palette="muted")

# Create figure and axis
fig, ax1 = plt.subplots(figsize=(8, 6))

# Axis 1 DISPARITY
ax1.set_ylabel('Gini coefficient', fontsize=10)
line1, = ax1.plot(df['year'], df['gini'], color='#C00000', linewidth=2)
ax1.tick_params(axis='y')
ax1.set_xlim(1980, 2024)
ax1.set_ylim(0, 0.6)
ax1.tick_params(axis='x', labelsize=9)
ax1.tick_params(axis='y', labelsize=8)

# Axis 2 GINI
ax2 = ax1.twinx()
ax2.set_ylabel('Urban-rural ratio', fontsize=10)
line2, = ax2.plot(df['year'], df['var_consumption'], color='#215C98', linewidth=2)
line3, = ax2.plot(df['year'], df['var_population'], color='#282828', linewidth=1, linestyle=":")
ax2.tick_params(axis='y')
ax2.set_ylim(0, 4)
ax2.tick_params(axis='y', labelsize=8)

# Title and grid
plt.text(0.02, 1.13, f'Inequality Trends in China', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.08, f'Urban-Rural Consumption Ratio and Gini Coefficient since 1980', fontsize=11, color="#3A3A3A", ha='left', transform=plt.gca().transAxes)
ax1.grid(axis='y', linestyle='-', alpha=0.5)

# Remove spines
for ax in (ax1, ax2):
    for spine_name, spine in ax.spines.items():
        if spine_name == 'bottom':
            spine.set_visible(True)
            spine.set_linewidth(0.5)
        else:
            spine.set_visible(False)

# Legend at bottom center
plt.plot([], [], color='#C00000', label='Gini coefficient')
plt.plot([], [], color='#215C98', label='Consumption ratio')
plt.plot([], [], color='#282828', label='Population ratio', linestyle=':')
plt.legend(
    loc='lower center',
    bbox_to_anchor=(0.5, -0.15),
    ncol=3,
    fontsize=8,
    frameon=False,
    handlelength=1,
    handleheight=1,
    borderpad=0.2,
    columnspacing=0.5
)

# Add Data Source
plt.text(0, -0.18, 'Data Source:', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')
space = " " * 23
plt.text(0, -0.18, space + 'National Bureau of Statistics of China (NBS), World Inequality Database (WID)', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Add Notes
plt.text(0, -0.21, 'Ratio:', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')
space = " " * 11
plt.text(0, -0.21, space + 'Urban-Rural Ratio measures the relative size between urban and rural for population and consumption', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Add Notes
plt.text(0, -0.24, 'Gini:', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')
space = " " * 9
plt.text(0, -0.24, space + 'Gini coefficient is calculated using post-tax national income to measure income inequality', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Adjust
plt.tight_layout()

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_NBS_Inequality_China.png")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Show it :)
plt.show()