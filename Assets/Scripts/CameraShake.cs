using UnityEngine;
using System.Collections;

[DefaultExecutionOrder(100)]
public class TopDownCameraShake : MonoBehaviour
{
    [Header("Normal Shake")]
    public float duration = 0.15f;
    public float strength = 0.15f;

    [Header("Death Impact")]
    public float deathDuration = 0.9f;
    public float deathStrength = 0.8f;
    public float deathRotation = 2f;
    public float impactFrequency = 25f;

    [Header("Slow Motion")]
    public bool useSlowMotion = true;
    [Range(0.05f, 1f)]
    public float slowMotionScale = 0.3f;
    public float slowMotionDuration = 0.6f;
    public float slowMotionRecovery = 0.4f;

    private TopDownCameraFollow follow;
    private Vector3 previousOffset;
    private float timer;
    private float currentDuration;
    private float currentStrength;
    private float currentRotation;
    private float shakeTime;

    private float originalTimeScale = 1f;
    private float originalFixedDeltaTime = 0.02f;

    private Coroutine slowMotionRoutine;

    private void Awake()
    {
        follow = GetComponent<TopDownCameraFollow>();
    }

    public void Shake()
    {
        timer = duration;
        currentDuration = duration;
        currentStrength = strength;
        currentRotation = 0.3f;
    }

    public void DeathShake()
    {
        timer = deathDuration;
        currentDuration = deathDuration;
        currentStrength = deathStrength;
        currentRotation = deathRotation;
        shakeTime = 0f;

        if (useSlowMotion)
        {
            if (slowMotionRoutine != null)
                StopCoroutine(slowMotionRoutine);

            slowMotionRoutine = StartCoroutine(DeathSlowMotion());
        }
    }

    private IEnumerator DeathSlowMotion()
    {
        originalTimeScale = Time.timeScale;
        originalFixedDeltaTime = Time.fixedDeltaTime;

        Time.timeScale = slowMotionScale;
        Time.fixedDeltaTime = originalFixedDeltaTime * slowMotionScale;

        yield return new WaitForSecondsRealtime(slowMotionDuration);

        float elapsed = 0f;
        float startScale = Time.timeScale;
        float recoveryDuration = Mathf.Max(0.01f, slowMotionRecovery);

        while (elapsed < recoveryDuration)
        {
            elapsed += Time.unscaledDeltaTime;

            float t = Mathf.Clamp01(elapsed / recoveryDuration);
            t = t * t * (3f - 2f * t);

            Time.timeScale = Mathf.Lerp(
                startScale,
                originalTimeScale,
                t
            );

            Time.fixedDeltaTime =
                originalFixedDeltaTime * Time.timeScale;

            yield return null;
        }

        Time.timeScale = originalTimeScale;
        Time.fixedDeltaTime = originalFixedDeltaTime;

        slowMotionRoutine = null;
    }

    private void LateUpdate()
    {
        float blend = follow != null && follow.smoothSpeed > 0f
            ? Mathf.Clamp01(follow.smoothSpeed * Time.deltaTime)
            : 1f;

        Vector3 basePosition =
            transform.position - previousOffset * (1f - blend);

        Quaternion baseRotation = follow != null
            ? Quaternion.Euler(
                follow.RotationX,
                follow.RotationY,
                follow.RotationZ
            )
            : transform.rotation;

        float intensity = currentDuration > 0f
            ? currentStrength * Mathf.Clamp01(timer / currentDuration)
            : 0f;

        shakeTime += Time.unscaledDeltaTime;

        float x = (Mathf.PerlinNoise(
            shakeTime * impactFrequency, 0f) - 0.5f) * 2f;

        float y = (Mathf.PerlinNoise(
            0f, shakeTime * impactFrequency) - 0.5f) * 2f;

        Vector3 shake = baseRotation *
            new Vector3(x, y, 0f) * intensity;

        transform.position = basePosition + shake;
        previousOffset = shake;

        if (intensity > 0f && currentRotation > 0f)
        {
            float roll = Mathf.Sin(shakeTime * impactFrequency)
                * currentRotation
                * Mathf.Clamp01(timer / currentDuration);

            transform.rotation = baseRotation *
                Quaternion.Euler(0f, 0f, roll);
        }
        else
        {
            transform.rotation = baseRotation;
        }

        timer = Mathf.Max(
            0f,
            timer - Time.unscaledDeltaTime
        );
    }

    private void OnDisable()
    {
        if (slowMotionRoutine != null)
        {
            StopCoroutine(slowMotionRoutine);
            slowMotionRoutine = null;

            Time.timeScale = originalTimeScale;
            Time.fixedDeltaTime = originalFixedDeltaTime;
        }
    }
}