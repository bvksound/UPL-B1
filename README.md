UPL-B1 Low Distortion Generator — Functional Description (Sheets 1–5)

The UPL-B1 is a digitally controlled, ultra-low-distortion sine-wave generator. It operates by forming a precisely tuned analog feedback loop based on two integrators, a loop inverter, a fine-tuning DAC, and an ultra-slow automatic level control system. The resulting sine wave is then routed through a calibrated output attenuator to the LOW DIST output connector.

The block diagram in Sheet 1 shows how the system is organized.
What follows is the working description of each functional block in the signal path.

⸻

1. Digital Control Interface (Data Link)

(Located in sheet 1)

At the heart of the module’s control architecture is the Data Link, which acts as the communication interface between the UPL main processor and all analog functions of the generator. A chain of serial-in/parallel-out registers receives configuration words via the UPL’s internal bus. Once a word is clocked in and latched, each bit becomes a control signal for:
	•	selecting RC networks inside the frequency-defining integrators,
	•	programming the 12-bit DAC used for fine frequency tuning,
	•	configuring the ALC’s track-and-hold behavior,
	•	setting the output level via the IMD attenuator.

In this way, the Data Link provides complete, deterministic configuration of the low-distortion generator through a simple serial interface.

⸻

2. First Loop Element: Integrator 2

(Located in sheet 4)

The oscillator loop begins with Integrator 2, which receives the feedback signal from the loop inverter. This block is a precision analog integrator with a set of relay- and switch-selectable RC networks. These RC combinations determine the coarse frequency range of the oscillator.

Because the transfer function of an integrator introduces a –90° phase shift, this element contributes the first quadrature shift in the loop. The output of this block is labelled SIN. It serves as both a phase-shifted signal for the next integrator and as a key reference for amplitude monitoring in the ALC.

⸻

3. Second Loop Element: Integrator 1, and the Loop Inverter

(Both located in sheet 3)

Integrator 1 — second 90° phase shift

The SIN signal from Integrator 2 is fed into Integrator 1, which is structurally similar—another precision op-amp stage with switchable RC networks.
This second integrator produces the COS signal, shifted by another –90°.
Together, the two integrators establish the total –180° shift required by the oscillator’s feedback loop.

Fine Frequency Tuning (DAC + Summing Amplifier)

A portion of the COS signal is routed into a 12-bit DAC system, whose output feeds a summing amplifier. This mechanism provides continuous fine frequency adjustment within each coarse RC range.
The UPL’s firmware writes a digital tuning word via the Data Link, and the DAC modifies the loop dynamics subtly to achieve precise output frequency control.

Loop Inverter — completes the oscillation path

The Loop Inverter receives signals from the fine-tuning circuit and the integrator chain and produces the required additional –180° phase inversion, closing the total loop phase at 360° (0° net).
The loop inverter also establishes the oscillator’s effective feedback gain, which is later stabilized by the amplitude control system.

The output of the loop inverter is fed back to Integrator 2, completing the analog oscillator core.

⸻

4. Amplitude Regulation: The Automatic Level Control (ALC)

(Located in sheet 5)

A precision sine-wave oscillator will naturally drift or saturate unless its amplitude is regulated. In the UPL-B1, this regulation is handled by the Automatic Level Control (ALC) system.

Amplitude Sampling and Track-and-Hold

A portion of the SIN waveform is extracted and fed into a track-and-hold detector.
This allows the ALC to operate cleanly over the full frequency range of the generator—including very low frequencies—where a conventional detector would otherwise create distortion or instability.

Precision Detection and Error Generation

The sampled waveform is rectified and converted into a DC level proportional to its amplitude.
A summing amplifier compares this value to an internally established reference representing the desired output level.

Slow, Low-Distortion Control Loop

The resulting error signal passes through carefully designed low-frequency filters.
These filters ensure that the ALC’s response is extremely slow—far outside the audio band—so that no gain modulation occurs within the audible range. This is critical for achieving the exceptionally low distortion performance of the UPL-B1.

VCA Gain Element

The filtered control voltage drives a voltage-controlled amplifier (VCA) in the main signal path.
When the amplitude is too low, the VCA’s gain increases; when too high, it decreases.
When equilibrium is reached, the loop gain of the oscillator is exactly unity, resulting in a stable, clean sine of precisely controlled amplitude.

The regulated sine now moves to the final output stage.

⸻

5. Output Level Setting: IMD Attenuator

(Located in sheet 2)

The final block is the IMD Attenuator, responsible for delivering calibrated output levels to the LOW DIST connector.
The attenuator uses relay-selected resistor networks combined with precision buffer amplification. Control bits from the Data Link determine the selected attenuation step.

Unlike the ALC-governed gain element, the IMD attenuator applies fixed, accurate attenuation values that do not interact with the oscillator’s internal amplitude regulation. This ensures:
	•	repeatable, calibration-grade output levels,
	•	reliable IMD and THD measurement conditions,
	•	and isolation of the internal oscillator loop from load-dependent variations.

The output of this attenuator is the module’s LOW DIST signal.

⸻

Complete Signal Flow (at a glance)
	1.	UPL processor configures the module via the Data Link (Sheet 1).
	2.	The signal enters Integrator 2 (Sheet 4) which adds the first –90° phase shift.
	3.	It then enters Integrator 1 (Sheet 3) for another –90° shift, producing COS.
	4.	The signal passes through the fine-tuning DAC and the Loop Inverter (Sheet 3), closing the loop.
	5.	The resulting oscillation is amplitude-stabilized by the ALC system (Sheet 5).
	6.	The regulated sine enters the IMD Attenuator (Sheet 2).
	7.	The final output appears as LOW DIST, ready for measurement applications.
