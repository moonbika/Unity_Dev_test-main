using UnityEngine;
using UnityEngine.Events;
using System.Collections;

public class ThrowProjectile : MonoBehaviour
{
    [Header("Projectile")]
    public Rigidbody projectilePrefab;
    public Transform throwPoint;
    public float launchForce = 15f;
    public float timeBetweenShots = 0.5f;

    [Header("Barrel Recoil")]
    public Transform barrelTransform;
    public float recoilDistance = 0.25f;
    public float recoilDuration = 0.06f;
    public float returnDuration = 0.15f;

    [Header("Camera Shake")]
    public TopDownCameraShake cameraShake;

    [Header("Events")]
    public UnityEvent OnShoot = new UnityEvent();

    private float nextTimeToFire;
    private Vector3 barrelInitialPosition;
    private Coroutine recoilRoutine;

    private void Awake()
    {
        if (barrelTransform != null)
            barrelInitialPosition = barrelTransform.localPosition;

        if (cameraShake == null)
            cameraShake = FindAnyObjectByType<TopDownCameraShake>();
    }

    private void Update()
    {
        if (Input.GetMouseButtonDown(0) &&
            Time.time >= nextTimeToFire)
        {
            ThrowProjectile1();
            nextTimeToFire = Time.time + timeBetweenShots;
        }
    }

    private void ThrowProjectile1()
    {
        if (projectilePrefab == null || throwPoint == null)
            return;

        Rigidbody projectile = Instantiate(
            projectilePrefab,
            throwPoint.position,
            throwPoint.rotation
        );

        projectile.linearVelocity = throwPoint.forward * launchForce;

        if (cameraShake != null)
            cameraShake.Shake();

        PlayBarrelRecoil();

        OnShoot.Invoke();
    }

    private void PlayBarrelRecoil()
    {
        if (barrelTransform == null)
            return;

        if (recoilRoutine != null)
            StopCoroutine(recoilRoutine);

        recoilRoutine = StartCoroutine(AnimateRecoil());
    }

    private IEnumerator AnimateRecoil()
    {
        Vector3 startPosition = barrelTransform.localPosition;

        Vector3 recoilPosition =
            barrelInitialPosition -
            Vector3.forward * recoilDistance;

        float elapsed = 0f;
        float duration = Mathf.Max(0.01f, recoilDuration);

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.Clamp01(elapsed / duration);
            t = 1f - Mathf.Pow(1f - t, 3f);

            barrelTransform.localPosition =
                Vector3.Lerp(startPosition, recoilPosition, t);

            yield return null;
        }

        barrelTransform.localPosition = recoilPosition;

        elapsed = 0f;
        duration = Mathf.Max(0.01f, returnDuration);

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.Clamp01(elapsed / duration);

            barrelTransform.localPosition =
                Vector3.Lerp(recoilPosition, barrelInitialPosition, t);

            yield return null;
        }

        barrelTransform.localPosition = barrelInitialPosition;
        recoilRoutine = null;
    }
}