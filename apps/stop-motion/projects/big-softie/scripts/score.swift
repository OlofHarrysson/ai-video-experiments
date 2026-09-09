import Foundation
import AVFoundation

// Original miniature score. The melody opens tentatively, warms at the play bow,
// becomes playful on the chase, and resolves as the dogs rest together.
let rate = 48000.0
let duration = 19.5
let engine = AVAudioEngine()
let piano = AVAudioUnitSampler()
let celesta = AVAudioUnitSampler()
let reverb = AVAudioUnitReverb()
engine.attach(piano); engine.attach(celesta); engine.attach(reverb)
let format = AVAudioFormat(standardFormatWithSampleRate: rate, channels: 2)!
engine.connect(piano, to: engine.mainMixerNode, format: format)
engine.connect(celesta, to: engine.mainMixerNode, format: format)
let bank = URL(fileURLWithPath:"/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls")
try piano.loadSoundBankInstrument(at:bank,program:0,bankMSB:UInt8(kAUSampler_DefaultMelodicBankMSB),bankLSB:0)
try celesta.loadSoundBankInstrument(at:bank,program:8,bankMSB:UInt8(kAUSampler_DefaultMelodicBankMSB),bankLSB:0)
piano.masterGain = -9; celesta.masterGain = -13
struct Event {let frame:Int64;let note:UInt8;let velocity:UInt8;let voice:Int;let on:Bool}
var events:[Event]=[]
func note(_ pitch:Int,_ time:Double,_ length:Double,_ velocity:Int = 62,_ voice:Int = 0){
 events.append(Event(frame:Int64(time*rate),note:UInt8(pitch),velocity:UInt8(velocity),voice:voice,on:true))
 events.append(Event(frame:Int64((time+length)*rate),note:UInt8(pitch),velocity:0,voice:voice,on:false))
}
let chords=[[50,57,62,66],[47,54,59,62],[43,55,59,62],[45,57,61,64],[50,57,62,66],[47,54,59,62],[43,55,59,62],[50,57,62,66]]
for bar in 0..<8 {
 let t=Double(bar)*2.0
 for (j,p) in chords[bar].enumerated(){note(p,t+Double(j)*0.24,1.2,bar==1 ? 42:49)}
 if bar>=4 && bar<6 {for (j,p) in chords[bar].enumerated(){note(p+12,t+1+Double(j)*0.20,0.44,42)}}
}
let melody:[(Int,Double,Double)]=[(74,0.25,0.28),(78,0.75,0.4),(81,1.25,0.55),(78,2.25,0.42),(76,3.0,0.6),(74,5.05,0.38),(78,5.55,0.35),(79,6.05,0.38),(81,6.55,0.7),(78,7.55,0.3),(81,8.55,0.25),(83,8.8,0.23),(86,9.05,0.4),(83,9.55,0.3),(81,10.05,0.25),(78,10.3,0.25),(76,10.55,0.35),(78,11.05,0.3),(81,11.55,0.5),(79,12.6,0.55),(78,13.3,0.6),(76,14.05,0.6),(78,14.8,0.65),(74,15.6,2.4)]
for (p,t,l) in melody {note(p,t,l,64,1)}
for (j,p) in [50,57,62,66].enumerated(){note(p,15.6+Double(j)*0.23,2.3,43)}
events.sort{$0.frame < $1.frame}
try engine.enableManualRenderingMode(.offline,format:format,maximumFrameCount:1024)
try engine.start()
let output=URL(fileURLWithPath:"assets/score.wav")
var file: AVAudioFile? = try AVAudioFile(forWriting:output,settings:format.settings)
let buffer=AVAudioPCMBuffer(pcmFormat:format,frameCapacity:1024)!
var cursor:Int64=0;var i=0;let total=Int64(duration*rate)
while cursor<total {
 while i<events.count && events[i].frame<=cursor {let e=events[i];let v=e.voice==0 ? piano:celesta;if e.on{v.startNote(e.note,withVelocity:e.velocity,onChannel:0)}else{v.stopNote(e.note,onChannel:0)};i+=1}
 let next=i<events.count ? events[i].frame:total
 let count=AVAudioFrameCount(min(1024,min(total-cursor,max(1,next-cursor))))
 let status=try engine.renderOffline(count,to:buffer)
 if status == .success {
  if let channels=buffer.floatChannelData {for c in 0..<2 {for f in 0..<Int(buffer.frameLength){let t=Double(cursor+Int64(f))/rate;let gain=Float(min(1,max(0,(19.5-t)/0.8)));channels[c][f] *= gain}}}
  try file!.write(from:buffer);cursor += Int64(count)
 }
}
file = nil
engine.stop()
print("Original score rendered: \(duration)s, 48 kHz stereo")
