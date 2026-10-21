/**
 * BioRig R29: EXPERIMENTAL (OFF unless deliberately enabled)
 * State-conditioned muscle-QP task allocation. NO force/torque/pose actuator.
 * Inputs are sensor readings, not fabricated anatomical load capacity.
 *
 * This function returns task weights only. It does not itself actuate the body.
 */
export function spinePriorityPolicy(s, c = {}) {
 const p = { activationLoadN:120, fullLoadN:420, neutralDeg:5,
   sFullDeg:20, maxSWeight:0.12, pelvisWorldCeiling:0.6,
   kP:30, kD:12, maxAccel:35, ...c };
 for (const k of ['stanceLoadN','spine01Lateral','spine02Lateral','spine01Rate','spine02Rate','spineIntent01','spineIntent02','existingPelvisWorldScale'])
   if (!Number.isFinite(s[k])) throw new TypeError('Missing/invalid state: '+k);
 if (!s.walking || !s.singleSupport) return {
   enabled:false, pairWeight:0, desiredRelativeAccel:0,
   pelvisWorldScale:s.existingPelvisWorldScale, priority:'native_nonwalking'
 };
 const clamp=(x,lo,hi)=>Math.max(lo,Math.min(hi,x));
 // Real load provides a confidence gate. Never invent a force or increase it.
 const contact=clamp((s.stanceLoadN-p.activationLoadN)/(p.fullLoadN-p.activationLoadN),0,1);
 // S-mode is the excess of *relative* lateral bending over intentional relative motion.
 // Do not suppress deliberate same-direction bending or independent axial rotation.
 const mismatch=(s.spine01Lateral-s.spineIntent01)-(s.spine02Lateral-s.spineIntent02);
 const rate=s.spine01Rate-s.spine02Rate;
 const dead=p.neutralDeg*Math.PI/180, full=p.sFullDeg*Math.PI/180;
 const excess=Math.sign(mismatch)*Math.max(0,Math.abs(mismatch)-dead);
 const span=Math.max(1e-6,full-dead);
 const urgency=clamp(Math.abs(excess)/span,0,1);
 const pairWeight=contact*urgency*p.maxSWeight;
 const desiredRelativeAccel=clamp(-p.kP*excess-p.kD*rate,-p.maxAccel,p.maxAccel);
 return {enabled:true,pairWeight,desiredRelativeAccel,
   pelvisWorldScale:Math.min(s.existingPelvisWorldScale,p.pelvisWorldCeiling),
   contactConfidence:contact,excessRelativeBendDeg:excess*180/Math.PI,
   priority:'foot_contact_and_com_before_relative_spine',
   warning:contact===0?'no_loaded_stance_contact':'none'};
}
