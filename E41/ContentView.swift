import SwiftUI
import UIKit
import UniformTypeIdentifiers
import Foundation

// Public API harness. Only generated fixture bytes are eligible for reading.
// No URL, path, userInfo, file content, device identifier or bookmark is logged.
struct E41Event: Codable {
    let sequence: Int
    let operation: String
    let outcome: String
    let scopeStarted: Bool?
    let errorDomain: String?
    let errorCode: Int?
}

@MainActor
final class E41Model: ObservableObject {
    static let fixtureName = "E41-fixture.txt"
    static let fixtureBytes = Data("E41 synthetic fixture v1\n".utf8)
    @Published var events: [E41Event] = []
    @Published var pickerMode: PickerMode?

    enum PickerMode: String, Identifiable {
        case exportFixture, openFixture
        var id: String { rawValue }
    }

    var fixtureURL: URL {
        FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
            .appendingPathComponent(Self.fixtureName)
    }

    func record(_ operation: String, _ outcome: String, scope: Bool? = nil, error: Error? = nil) {
        let nsError = error as NSError?
        events.append(E41Event(sequence: events.count + 1, operation: operation,
                               outcome: outcome, scopeStarted: scope,
                               errorDomain: nsError?.domain, errorCode: nsError?.code))
    }

    func baseline() {
        do {
            try Self.fixtureBytes.write(to: fixtureURL, options: .atomic)
            let value = try Data(contentsOf: fixtureURL)
            record("own_container_baseline", value == Self.fixtureBytes ? "fixture_match" : "fixture_mismatch")
        } catch { record("own_container_baseline", "io_error", error: error) }
    }

    func exportFixture() {
        baseline()
        guard FileManager.default.fileExists(atPath: fixtureURL.path) else { return }
        pickerMode = .exportFixture
    }

    func selected(_ urls: [URL], mode: PickerMode) {
        guard mode == .openFixture else {
            record("fixture_export", "picker_destination_selected")
            return
        }
        guard urls.count == 1, let url = urls.first, url.isFileURL,
              url.lastPathComponent == Self.fixtureName else {
            record("external_fixture", "ineligible_selection_no_read")
            return
        }
        let granted = url.startAccessingSecurityScopedResource()
        guard granted else {
            // False is recorded as scope unavailable, not assumed kernel denial.
            record("external_fixture", "scope_not_started_no_read", scope: false)
            return
        }
        defer { url.stopAccessingSecurityScopedResource() }
        let coordinator = NSFileCoordinator(filePresenter: nil)
        var coordinationError: NSError?
        var outcome = "coordination_did_not_execute"
        var readError: Error?
        coordinator.coordinate(readingItemAt: url, options: [], error: &coordinationError) { coordinatedURL in
            do {
                let attributes = try coordinatedURL.resourceValues(forKeys:
                    [.isRegularFileKey, .isSymbolicLinkKey, .fileSizeKey])
                guard attributes.isRegularFile == true, attributes.isSymbolicLink != true,
                      attributes.fileSize == Self.fixtureBytes.count else {
                    outcome = "ineligible_resource_no_content_read"
                    return
                }
                let handle = try FileHandle(forReadingFrom: coordinatedURL)
                defer { try? handle.close() }
                let value = try handle.read(upToCount: Self.fixtureBytes.count + 1) ?? Data()
                outcome = value == Self.fixtureBytes ? "fixture_match" : "fixture_mismatch_not_retained"
            } catch {
                outcome = "io_error"
                readError = error
            }
        }
        if let error = coordinationError {
            record("external_fixture", "coordination_error", scope: true, error: error)
        } else {
            record("external_fixture", outcome, scope: true, error: readError)
        }
    }

    func cancelled(_ mode: PickerMode) {
        record(mode == .openFixture ? "external_fixture" : "fixture_export",
               "user_cancelled_no_resource_read")
    }

    var sanitizedJSON: String {
        struct Result: Encodable {
            let experiment: String
            let environment: String
            let systemVersion: String
            let events: [E41Event]
        }
        #if targetEnvironment(simulator)
        let environment = "Apple_simulator_not_physical_iPad"
        #else
        let environment = "device_app_runtime_not_host_simulation"
        #endif
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let result = Result(experiment: "E41", environment: environment,
                            systemVersion: UIDevice.current.systemVersion, events: events)
        guard let data = try? encoder.encode(result) else { return "{}" }
        return String(decoding: data, as: UTF8.self)
    }
}

struct E41Picker: UIViewControllerRepresentable {
    let model: E41Model
    let mode: E41Model.PickerMode

    func makeCoordinator() -> Coordinator { Coordinator(model: model, mode: mode) }

    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let picker: UIDocumentPickerViewController
        if mode == .exportFixture {
            picker = UIDocumentPickerViewController(forExporting: [model.fixtureURL], asCopy: true)
        } else {
            picker = UIDocumentPickerViewController(forOpeningContentTypes: [.plainText], asCopy: false)
        }
        picker.allowsMultipleSelection = false
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ controller: UIDocumentPickerViewController, context: Context) {}

    final class Coordinator: NSObject, UIDocumentPickerDelegate {
        let model: E41Model
        let mode: E41Model.PickerMode
        init(model: E41Model, mode: E41Model.PickerMode) { self.model = model; self.mode = mode }
        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            model.selected(urls, mode: mode)
            model.pickerMode = nil
        }
        func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) {
            model.cancelled(mode)
            model.pickerMode = nil
        }
    }
}

struct ContentView: View {
    @StateObject private var model = E41Model()
    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Select only the generated E41-fixture.txt in a dedicated test folder. Paths and contents are not logged.")
                Button("1. Own-container baseline") { model.baseline() }
                Button("2. Export synthetic fixture") { model.exportFixture() }
                Button("3. Open fixture or cancel") { model.pickerMode = .openFixture }
                Text("Repeat baseline/open/cancel twice. Cancellation is unavailability, not a proven sandbox denial.")
                    .font(.footnote)
                ScrollView {
                    Text(model.sanitizedJSON).font(.system(.caption, design: .monospaced)).textSelection(.enabled)
                }
            }
            .padding()
            .navigationTitle("E41 permission contract")
            .sheet(item: $model.pickerMode) { mode in E41Picker(model: model, mode: mode) }
        }
    }
}
