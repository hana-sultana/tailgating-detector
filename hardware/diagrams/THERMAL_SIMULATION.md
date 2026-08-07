# Thermal Simulation

## Why simulate thermal performance?

The Raspberry Pi 5's SoC dissipates around 6 W under sustained YOLO
inference. Enclosed in a plastic case inside a parked car that can hit
60 °C in Texas summer, the Pi is working against a bad starting
temperature with limited paths for heat to escape. If the SoC crosses
85 °C it throttles itself, which means detection slows down or stops
right when it matters. A thermal simulation lets us catch this problem
in software before printing plastic and mounting hardware in a car.

## Environmental context

The system is designed for use in Houston, Texas. Local summer highs
routinely reach 105 °F (40.5 °C), and a parked car's interior can
exceed 60 °C in direct sun. The 25 °C ambient value used in the
simulation below therefore represents a mild baseline, not a
worst-case operating condition. A follow-up run should sweep ambient
from 25 °C to 60 °C to characterize warm-weather performance.

## Approach

Ran a **steady-state heat transfer (solid conduction) analysis** in
SimScale using the sealed enclosure geometry
(`hardware/cad/case_combined.stl`).

The physics is deliberately simplified compared to a full conjugate
heat transfer simulation, which would also model the internal air
flow. STL files export a single triangle mesh, so SimScale sees the
enclosure as one solid body without a separate fluid region. Proper
conjugate heat transfer would need the case rebuilt as a multi-body
STEP model in Fusion 360. Solid-only conduction is a reasonable
first-order approach for looking at how heat spreads through the
plastic, but as documented in the results section below, it is not
sufficient by itself to answer the practical question of whether the
case works.

## Setup

| Parameter | Value | Notes |
|---|---|---|
| Physics | Heat Transfer (solid conduction) | Steady-state, linear |
| Geometry | `case_combined.stl` | Sealed base + lid, scaled to mm |
| Material | PET (thermal conductivity 0.2 W/m·K) | PETG proxy; within ~5% of PETG values |
| Heat source | 26,667 W/m² on interior floor face | 6 W spread over the case floor area |
| Heat sink | Fixed 25 °C on outer walls | First-order convection substitute |
| Mesh | ~450k cells, coarse (fineness = 1) | Sufficient for first-order thermal |

## Results

![Case floor temperature distribution](../hardware/cad/cfd_result.png)

The temperature field on the case floor shows the expected conduction
pattern: heat concentrates in the center (red) and spreads outward
through the plastic to the cooler outer walls (blue) where the
ambient boundary pulls heat away. The gradient is smooth and
physically consistent with 2D conduction from a distributed source.

## Important finding: results are unphysical

The color scale on the result shows a peak temperature of about
**1881 K (1608 °C)** at the center. PET plastic melts at around
260 °C, so this result cannot represent a real operating condition.
The simulation is telling us something real, but it is not "the case
gets to 1600 °C."

What actually happened: the model has a fixed 6 W of heat entering
through the floor and only conductive paths through the plastic walls
to a 25 °C boundary. The plastic is a poor conductor
(0.2 W/m·K). With no convection, no radiation, and no airflow through
the vents, the only way for the math to balance 6 W in against 6 W
out is for the temperature gradient to become extreme. The solver
kept climbing until it hit whatever temperature was needed to push
the heat through, ignoring that the material would have melted long
before that.

The takeaway is that solid-only conduction on its own is not a
sufficient model for this enclosure. The vents and the active cooler
are not incidental features that could be simplified away — they are
doing most of the cooling work. Any thermal result that ignores them
will over-predict internal temperature to the point of being
non-physical.

## Limitations

- **No airflow modeled.** This is the dominant limitation and the
  reason the result above is not physically meaningful. Real
  ventilation through the top vent slots plus the Pi 5 Active Cooler
  fan will significantly improve cooling.
- **No radiation modeled.** At the extreme temperatures the solver
  reached, radiative heat loss would be a major term in reality.
- **Uniform floor heat flux.** The real SoC is a 15 mm × 15 mm hot
  spot, not a distributed source. In a properly cooled model, the
  actual chip location would be hotter than what the simulation shows
  at that location.
- **Ambient boundary is idealized.** A parked car interior doesn't
  behave like a magic 25 °C wall; a full model would apply a
  convective boundary tied to expected in-cabin air temperature, and
  in Houston that boundary temperature is closer to 40–60 °C than
  25 °C.
- **Not validated against measurement.** No physical prototype was
  available to compare against.

## Future work

- Rebuild the enclosure in Fusion 360 as a proper solid + fluid
  assembly, exported as STEP, and re-run as conjugate heat transfer
  with the internal air region and vent openings modeled explicitly.
- Add the active cooler fan as a defined flow boundary once the fluid
  region exists.
- Sweep ambient temperature from 25 °C to 60 °C to bracket
  summer-parking behavior in Houston.
- Instrument the printed prototype with `vcgencmd measure_temp` and
  run a 30-minute sustained YOLO load. Compare the measured SoC
  temperature against the (updated) simulation. This is the real
  validation step.
