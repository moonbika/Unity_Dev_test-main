using System.Collections;
using UnityEngine;
using UnityEngine.Rendering;

public class DamageVolumeTrigger : MonoBehaviour
{
    [Header("Damage Effect")]
    public Volume damageVolume;
    public float duration = 0.25f;

    [Header("Camera Shake")]
    public TopDownCameraShake cameraShake;

    private Coroutine routine;

    private void Awake()
    {
        if (damageVolume != null)
            damageVolume.weight = 0f;

        if (cameraShake == null)
            cameraShake = FindAnyObjectByType<TopDownCameraShake>();
    }

    public void TriggerDamage()
    {
        if (cameraShake != null)
            cameraShake.Shake();

        if (damageVolume == null)
            return;

        if (routine != null)
            StopCoroutine(routine);

        routine = StartCoroutine(ShowDamage());
    }

    private IEnumerator ShowDamage()
    {
        damageVolume.weight = 1f;

        float elapsed = 0f;
        float effectDuration = Mathf.Max(0.01f, duration);

        while (elapsed < effectDuration)
        {
            elapsed += Time.unscaledDeltaTime;

            damageVolume.weight =
                1f - Mathf.Clamp01(elapsed / effectDuration);

            yield return null;
        }

        damageVolume.weight = 0f;
        routine = null;
    }

    private void OnDisable()
    {
        if (routine != null)
        {
            StopCoroutine(routine);
            routine = null;
        }

        if (damageVolume != null)
            damageVolume.weight = 0f;
    }
}