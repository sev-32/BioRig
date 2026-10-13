# Negative results — do not silently reintegrate

These results are real 3-second MuJoCo branches using the exact R589 native body, which initially starts arms-out. They were **NOT promoted**.

- Forcing the right shoulder toward -55° brought a right arm load of 8 N at 3 s, but also produced a **141.5 N impact** and 21 right-arm contact toggles. Rejected.
- Strong left shoulder braking reduced left seat impacts to zero, but shifted collisions to the **right arm** (~79–84 N, 31–33 toggles) and frequently increased neck deviation beyond 5°. Rejected.
- Bilaterally strong muscle recruitment did not solve coupled contact: left peak ~104 N, 43 contact transitions, and ~12° head deviation. Rejected.
- Changing the rectangular seat half-width from the frozen 0.28 m to 0.34/0.38 m generated pathological **multi-kilonewton** arm impacts (approximately 9–16 kN). Widening was not a legitimate improvement; geometry and penetration must be jointly authored. Rejected.
- A naïve restart from recorded qpos/qvel/act without the *original neutral pose reference* or allocator state generated a new 82.7 N arm impact and 5.57° head deviation over 4 s, even though the original continuous 12..24s interval has no contact toggles. The corrected state restorer passes independent replay, and a controller must not silently redefine its reference from the settled pose.

The physical insight: torso, head, both shoulder actuators, and sharp seat-edge contacts are coupled. Optimizing one arm contact force in isolation can redistribute instability to the other side. More gain or contact stiffness alone is not a solution.

**R590's accepted scope** is the physical initial-condition correction for already seated equilibrium tests, not a claim that these failed dynamic landing configurations became biologically correct.
