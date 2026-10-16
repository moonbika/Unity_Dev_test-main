using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using Unity.Profiling;
using UnityEngine;

/// <summary>
/// Drag onto an active GameObject in the gameplay scene in each project version.
/// Runs a warmup, measures for a fixed duration, and writes one CSV summary.
/// Designed for Unity versions with Unity.Profiling.ProfilerRecorder (Unity 2020.2+).
/// </summary>
public sealed class UnityPerformanceBenchmark : MonoBehaviour
{
    [Header("Run settings")]
    [Tooltip("Use a different label for each project/build, e.g. Original and V2.")]
    [SerializeField] private string buildLabel = "V2";
    [Min(0f)] [SerializeField] private float warmupSeconds = 5f;
    [Min(5f)] [SerializeField] private float measurementSeconds = 30f;

    private ProfilerRecorder drawCallsRecorder;
    private ProfilerRecorder batchesRecorder;
    private ProfilerRecorder setPassRecorder;
    private ProfilerRecorder trianglesRecorder;
    private ProfilerRecorder mainThreadRecorder;
    private ProfilerRecorder totalCpuFrameRecorder;
    private ProfilerRecorder gpuFrameRecorder;

    private readonly List<double> frameTimesMs = new List<double>(2400);
    private bool measuring;
    private bool completed;
    private float warmupElapsed;
    private float measuredElapsed;
    private double frameTimeSumMs;
    private double drawCallsSum;
    private double batchesSum;
    private double setPassSum;
    private double trianglesSum;
    private double mainThreadSumNs;
    private double totalCpuFrameSumNs;
    private double gpuFrameSumNs;
    private int frameCount;
    private int drawCallsSamples;
    private int batchesSamples;
    private int setPassSamples;
    private int trianglesSamples;
    private int mainThreadSamples;
    private int totalCpuFrameSamples;
    private int gpuFrameSamples;

    private void OnEnable()
    {
        drawCallsRecorder = TryStartRecorder("Draw Calls Count");
        batchesRecorder = TryStartRecorder("Batches Count");
        setPassRecorder = TryStartRecorder("SetPass Calls Count");
        trianglesRecorder = TryStartRecorder("Triangles Count");
        mainThreadRecorder = TryStartRecorder("CPU Main Thread Frame Time");
        totalCpuFrameRecorder = TryStartRecorder("CPU Total Frame Time");
        gpuFrameRecorder = TryStartRecorder("GPU Frame Time");
    }

    private void Update()
    {
        if (completed)
            return;

        float delta = Time.unscaledDeltaTime;

        if (!measuring)
        {
            warmupElapsed += delta;
            if (warmupElapsed >= warmupSeconds)
            {
                measuring = true;
                measuredElapsed = 0f;
                frameTimesMs.Clear();
                Debug.Log($"[Benchmark] Measuring '{buildLabel}' for {measurementSeconds:0} seconds now. Keep the same gameplay scenario running.");
            }
            return;
        }

        measuredElapsed += delta;
        double frameMs = delta * 1000.0;
        frameTimeSumMs += frameMs;
        frameTimesMs.Add(frameMs);
        frameCount++;

        Accumulate(drawCallsRecorder, ref drawCallsSum, ref drawCallsSamples);
        Accumulate(batchesRecorder, ref batchesSum, ref batchesSamples);
        Accumulate(setPassRecorder, ref setPassSum, ref setPassSamples);
        Accumulate(trianglesRecorder, ref trianglesSum, ref trianglesSamples);
        Accumulate(mainThreadRecorder, ref mainThreadSumNs, ref mainThreadSamples);
        Accumulate(totalCpuFrameRecorder, ref totalCpuFrameSumNs, ref totalCpuFrameSamples);
        Accumulate(gpuFrameRecorder, ref gpuFrameSumNs, ref gpuFrameSamples);

        if (measuredElapsed >= measurementSeconds)
            FinishBenchmark();
    }

    private static ProfilerRecorder TryStartRecorder(string statName)
    {
        try
        {
            return ProfilerRecorder.StartNew(
                ProfilerCategory.Render,
                statName,
                1,
                ProfilerRecorderOptions.Default);
        }
        catch (Exception exception)
        {
            Debug.LogWarning($"[Benchmark] Could not start profiler counter '{statName}': {exception.Message}");
            return default;
        }
    }

    private static void Accumulate(ProfilerRecorder recorder, ref double sum, ref int samples)
    {
        if (!recorder.Valid)
            return;

        long value = recorder.LastValue;
        if (value < 0)
            return;

        sum += value;
        samples++;
    }

    private void FinishBenchmark()
    {
        completed = true;
        measuring = false;

        double averageFrameMs = frameCount > 0 ? frameTimeSumMs / frameCount : 0.0;
        double averageFps = measuredElapsed > 0f ? frameCount / (double)measuredElapsed : 0.0;
        double worstFrameMs = 0.0;
        double p95FrameMs = 0.0;

        if (frameTimesMs.Count > 0)
        {
            frameTimesMs.Sort();
            worstFrameMs = frameTimesMs[frameTimesMs.Count - 1];
            int p95Index = Mathf.Clamp(Mathf.CeilToInt(frameTimesMs.Count * 0.95f) - 1, 0, frameTimesMs.Count - 1);
            p95FrameMs = frameTimesMs[p95Index];
        }

        string dateStamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture);
        string safeLabel = MakeSafeFileName(string.IsNullOrWhiteSpace(buildLabel) ? "Build" : buildLabel.Trim());
        string fileName = $"TechArtBenchmark_{safeLabel}_{DateTime.Now:yyyyMMdd_HHmmss}.csv";
        string header = "BuildLabel,UnityVersion,Date,Resolution,Quality,GraphicsDevice,VSyncCount,WarmupSeconds,MeasuredSeconds,Frames,AverageFPS,AverageFrameTimeMs,P95FrameTimeMs,WorstFrameTimeMs,AverageCPU_MainThreadMs,AverageCPU_TotalFrameMs,AverageGPUFrameMs,AverageDrawCalls,AverageBatches,AverageSetPassCalls,AverageTriangles";

        string row = string.Join(",", new string[]
        {
            Csv(buildLabel),
            Csv(Application.unityVersion),
            Csv(dateStamp),
            Csv(Screen.width + "x" + Screen.height),
            Csv(GetQualityName()),
            Csv(SystemInfo.graphicsDeviceName),
            QualitySettings.vSyncCount.ToString(CultureInfo.InvariantCulture),
            F2(warmupSeconds),
            F2(measuredElapsed),
            frameCount.ToString(CultureInfo.InvariantCulture),
            F2(averageFps),
            F2(averageFrameMs),
            F2(p95FrameMs),
            F2(worstFrameMs),
            AverageOrNA(mainThreadSumNs, mainThreadSamples, 1e-6),
            AverageOrNA(totalCpuFrameSumNs, totalCpuFrameSamples, 1e-6),
            AverageOrNA(gpuFrameSumNs, gpuFrameSamples, 1e-6),
            AverageOrNA(drawCallsSum, drawCallsSamples, 1.0),
            AverageOrNA(batchesSum, batchesSamples, 1.0),
            AverageOrNA(setPassSum, setPassSamples, 1.0),
            AverageOrNA(trianglesSum, trianglesSamples, 1.0)
        });

        string path;
        try
        {
            // In a standalone build, this is the folder beside the executable.
            // In the Editor, it is the Unity project root.
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            Directory.CreateDirectory(root);
            path = Path.Combine(root, fileName);
            File.WriteAllText(path, header + Environment.NewLine + row + Environment.NewLine);
        }
        catch (Exception writeException)
        {
            // Fallback for folders where the build/project directory is not writable.
            string fallbackFolder = Application.persistentDataPath;
            Directory.CreateDirectory(fallbackFolder);
            path = Path.Combine(fallbackFolder, fileName);
            File.WriteAllText(path, header + Environment.NewLine + row + Environment.NewLine);
            Debug.LogWarning($"[Benchmark] Could not write beside the build: {writeException.Message}. Used persistent data folder instead.");
        }

        Debug.Log($"[Benchmark] Complete. CSV: {path}\n" +
                  $"Average FPS: {F2(averageFps)} | Average frame time: {F2(averageFrameMs)} ms | " +
                  $"Draw calls: {AverageOrNA(drawCallsSum, drawCallsSamples, 1.0)} | " +
                  $"Batches: {AverageOrNA(batchesSum, batchesSamples, 1.0)} | " +
                  $"SetPass: {AverageOrNA(setPassSum, setPassSamples, 1.0)}");

        ReleaseRecorders();
    }

    private static string AverageOrNA(double sum, int samples, double scale)
    {
        return samples > 0
            ? (sum / samples * scale).ToString("F2", CultureInfo.InvariantCulture)
            : "N/A";
    }

    private static string F2(double value)
    {
        return value.ToString("F2", CultureInfo.InvariantCulture);
    }

    private static string Csv(string value)
    {
        value = value ?? string.Empty;
        return "\"" + value.Replace("\"", "\"\"") + "\"";
    }

    private static string MakeSafeFileName(string value)
    {
        foreach (char invalid in Path.GetInvalidFileNameChars())
            value = value.Replace(invalid, '_');
        return value;
    }

    private static string GetQualityName()
    {
        string[] qualityNames = QualitySettings.names;
        int level = QualitySettings.GetQualityLevel();
        return qualityNames != null && level >= 0 && level < qualityNames.Length
            ? qualityNames[level]
            : "Unknown";
    }

    private void OnDisable()
    {
        ReleaseRecorders();
    }

    private void OnDestroy()
    {
        ReleaseRecorders();
    }

    private void ReleaseRecorders()
    {
        Release(ref drawCallsRecorder);
        Release(ref batchesRecorder);
        Release(ref setPassRecorder);
        Release(ref trianglesRecorder);
        Release(ref mainThreadRecorder);
        Release(ref totalCpuFrameRecorder);
        Release(ref gpuFrameRecorder);
    }

    private static void Release(ref ProfilerRecorder recorder)
    {
        if (recorder.Valid)
            recorder.Dispose();
        recorder = default;
    }
}
