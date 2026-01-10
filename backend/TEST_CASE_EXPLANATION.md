# Test Case Explanation: Banff SAR Scenario

## Test Scenario

### Input Parameters
- **Location:** Banff, Alberta (51.1784° N, 115.5708° W)
- **Subject:** 20-year-old male, medium experience
- **Last Seen:** 08:00 (4 hours ago)
- **Current Time:** 12:00
- **Search Radius:** 5km
- **Grid Resolution:** 100m cells

## What Happens When You Run the Test

### 1. System Processing (8-10 seconds)

```
Request → Backend Processing
├── Weather API Call (Open-Meteo)
│   └── Fetches: temperature, precipitation, wind, clouds
│
├── Elevation API Call (Open-Elevation)  
│   ├── Fetches elevation for 10,000 grid points
│   ├── Batch requests (100 points at a time)
│   └── Takes ~8 seconds for full grid
│
├── Terrain Model Creation
│   ├── Creates 100x100 grid (5km radius)
│   ├── Calculates slopes from elevation
│   └── Identifies terrain features
│
├── Behavioral Model Application
│   ├── Age-based travel rate: ~450m per 15min (20yo male)
│   ├── Medium experience modifiers
│   └── Time-based behavior changes
│
└── Probability Evolution (49 snapshots)
    ├── T+0h: 100% at last known location
    ├── T+1h: Spreading (panic phase)
    ├── T+4h: Current time estimate
    └── T+16h: Future projection
```

### 2. Weather Integration

**Real-time fetch from Banff:**
- Temperature: Likely -5°C to -15°C (January)
- Precipitation: Possible snow
- Wind: Mountain conditions

**Impact on predictions:**
- Cold weather: 0.7x movement speed
- Snow: 0.6-0.8x movement speed  
- Clear: 1.0x movement speed

### 3. Elevation Impact

**Banff terrain characteristics:**
- Base elevation: ~1,463m (townsite)
- Surrounding peaks: 1,800-2,800m
- Steep mountain slopes: 20-40° grades

**Movement effects:**
- Flat (0-5°): Normal speed
- Moderate uphill (10-20°): 0.7x speed
- Steep uphill (25-40°): 0.4x speed
- Downhill: 1.1x speed (easier)

### 4. Behavioral Analysis (20-year-old male)

#### Physical Capabilities
- **High fitness:** Can cover ~400-500m per 15 minutes
- **Good endurance:** Sustained effort for 8-12 hours
- **Youth advantage:** Quick recovery, high panic threshold

#### Experience Level (Medium)
- **Trail following:** 60% probability
- **Navigation:** Moderate skills
- **Risk-taking:** Higher than older subjects
- **Signal seeking:** May climb for cell reception

#### Time-Based Behavior Changes

**0-3 Hours (Panic Phase):**
- Movement: Erratic, fast-paced
- Direction: Random or uphill (cell signal)
- Speed: 130% of normal (panic multiplier)
- Decision-making: Poor, emotional

**3-6 Hours (Transition):**
- Movement: More rational
- Direction: Following linear features (trails, ridges)
- Speed: Normal to slower
- Decision-making: Improving

**6-12 Hours (Exhaustion Phase):**
- Movement: Significantly slower
- Direction: Seeking shelter
- Speed: 60-80% of normal
- Decision-making: Survival-focused

**12+ Hours (Shelter Phase):**
- Movement: Minimal
- Direction: Staying put
- Speed: 30% of normal
- Decision-making: Conserving energy

## Expected Output Breakdown

### Metadata Section
```json
{
  "request_id": "abc-123-def",
  "metadata": {
    "grid_size": 100,
    "grid_resolution_m": 100.0,
    "search_radius_km": 5.0,
    "total_snapshots": 49,
    "subject_age": 20,
    "subject_experience": "medium",
    "weather_conditions": "-8.5°C, clear",
    "weather_impact": "0.70x movement speed"
  }
}
```

**Interpretation:**
- 10,000 grid cells covering 100km²
- 49 time snapshots (every 15 min from T+0 to T+12 future)
- Cold weather slowing movement by 30%

### Snapshots Timeline

#### T+0 Hours (08:00 - Last Known Location)
```
Max probability: 1.0000 (100%)
Cells with probability: 1
Status: Subject is here with 100% certainty
```

#### T+1 Hour (09:00 - Initial Movement)
```
Max probability: 0.1234 (~12%)
Cells with probability: ~50
Status: Probability spreading in ~450m radius
        High panic, erratic movement
```

**Why spreading?**
- In 1 hour, subject could move ~1.8km in any direction
- Grid cells within this range get probability
- More cells = lower individual probability

#### T+4 Hours (12:00 - CURRENT TIME)
```
Max probability: 0.0089 (~0.89%)
Cells with probability: ~500
Status: Subject could be in any of these 500 locations
        Transition from panic to exhaustion
```

**Why so spread out?**
- In 4 hours, subject could be anywhere within 7km
- That's ~5,000 possible 100m cells
- Only cells with >0.01% probability shown
- Highest probability cells are:
  * Near trails (90% of subjects)
  * On ridgelines (signal seeking)
  * Sheltered areas (weather protection)

#### T+8 Hours (16:00 - Future Projection)
```
Max probability: 0.0034 (~0.34%)
Cells with probability: ~800
Status: Maximum spread, exhaustion phase beginning
```

#### T+16 Hours (00:00 - Next Day)
```
Max probability: 0.0012 (~0.12%)
Cells with probability: ~1000
Status: Subject likely sheltering, minimal movement
```

### Top 10 Probable Locations (at T+4)

**Example output:**
```
1. Probability: 0.0089 (0.89%)
   Location: 51.1798°N, 115.5710°W
   Elevation: 1,520m
   Distance: 0.15km from LKL
   
2. Probability: 0.0076 (0.76%)
   Location: 51.1812°N, 115.5695°W
   Elevation: 1,485m
   Distance: 0.31km from LKL

... (8 more locations)
```

**Why these locations?**
1. **Near last known location** - highest prior probability
2. **On/near trails** - 3-5x attraction factor
3. **Moderate elevation** - easier travel
4. **Sheltered aspects** - weather protection
5. **Linear features** - ridges, drainages

## Probability Interpretation

### What the Numbers Mean

**0.89% probability:**
- NOT "0.89% chance subject is here"
- ACTUALLY "This cell has 0.89% of total probability mass"

**Cumulative approach:**
- Top 10 cells: ~5% of total probability
- Top 100 cells: ~30% of total probability
- Top 500 cells: ~80% of total probability

**Search strategy:**
- Search high-probability cells first
- Cover top 100 cells = 30% chance of success
- Cover top 500 cells = 80% chance of success

### Confidence Levels

After 4 hours with 5km radius:
- **High confidence (>0.5%):** ~20 cells
- **Medium confidence (>0.1%):** ~150 cells
- **Low confidence (>0.01%):** ~500 cells

## Search Recommendations from Output

### Priority 1: Trail Corridors
- Check all trails within 5km
- 90% of lost persons found within 500m of trails
- Young males: High trail-following tendency

### Priority 2: Elevated Viewpoints
- Check peaks, ridges, open areas
- 20-year-old males often seek cell signal
- Higher elevation = better signal attempt

### Priority 3: Sheltered Areas
- Creeks, rock overhangs, tree clusters
- Cold weather = seeking protection
- After 4 hours, may be resting

### Priority 4: Linear Features
- Follow drainages, ridgelines
- Natural navigation aids
- Easy walking paths

## Why This System Works

### 1. Real Data
- ✅ Actual Banff elevation (1,463-2,800m)
- ✅ Real weather conditions (temperature, wind)
- ✅ Validated behavior patterns (SAR research)

### 2. Age/Sex Specificity
- 20yo male: Different from 60yo female
- Faster travel rate
- Higher risk-taking
- Better physical condition

### 3. Time Evolution
- Behavior changes over time
- Panic → Rationality → Exhaustion → Shelter
- Movement patterns adapt

### 4. Environmental Factors
- Weather slows movement
- Steep terrain limits travel
- Trails attract movement
- Sheltered areas provide refuge

## How to Run the Test

```bash
# 1. Start the server (if not running)
cd /Users/lucas/projects/beacon-ai/backend
./start.sh

# 2. Run validation (optional)
./validate_system.sh

# 3. Run the test
python3 test_banff_case.py
```

## Expected Runtime

- API request: 8-10 seconds (elevation fetch)
- Subsequent requests: 0.5-1 second (cached)
- Output display: ~2 seconds
- **Total: ~10-12 seconds first run**

## Success Indicators

✅ **System working if you see:**
- Request ID generated
- Weather conditions fetched
- Elevation data from API
- 49 snapshots generated
- Top 10 locations listed
- Search recommendations provided

❌ **Problems if you see:**
- Connection error → Server not running
- Timeout → Server crashed
- Syntax error → Code issue
- 500 error → Backend exception

## Real-World Context

**In actual SAR operation:**
- This output would guide search teams
- High-probability cells searched first
- Snapshots show predicted movement over time
- Weather impact factored into decisions
- Regular updates as new info arrives

**For Banff specifically:**
- Mountainous terrain is challenging
- Cold weather is life-threatening
- Cell signal spotty (encourages uphill movement)
- Many trails (high attraction factor)
- Wildlife concerns (bears, cougars)

This test validates the entire system works end-to-end with real data for a realistic SAR scenario.
