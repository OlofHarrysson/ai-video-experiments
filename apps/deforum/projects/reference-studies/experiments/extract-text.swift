// Read-only OCR of frames listed in a video_review.py JSON manifest.
// Usage: swift extract-text.swift REVIEW_JSON OUTPUT_JSON
import Foundation
import Vision

let manifest = URL(fileURLWithPath: CommandLine.arguments[1])
let destination = URL(fileURLWithPath: CommandLine.arguments[2])
guard !FileManager.default.fileExists(atPath: destination.path) else {
    fatalError("Refusing to overwrite an earlier OCR result")
}
let data = try JSONSerialization.jsonObject(with: Data(contentsOf: manifest)) as! [String: Any]
var rows: [[String: Any]] = []
for frame in data["frames"] as! [[String: Any]] {
    let path = manifest.deletingLastPathComponent().appendingPathComponent(frame["file"] as! String)
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    try VNImageRequestHandler(url: path).perform([request])
    let words: [[String: Any]] = (request.results ?? []).compactMap { observation in
        guard let candidate = observation.topCandidates(1).first else { return nil }
        return ["text": candidate.string, "confidence": candidate.confidence]
    }
    rows.append(["time_seconds": frame["time_seconds"]!, "file": path.path, "observations": words])
}
let output: [String: Any] = ["method": "Apple Vision accurate OCR; machine candidates require visual review",
                            "source_review": manifest.path, "frames": rows]
try JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted, .sortedKeys]).write(to: destination)
print("Saved OCR for \(rows.count) sampled frames")
