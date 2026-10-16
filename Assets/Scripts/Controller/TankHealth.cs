using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;
using System.Collections;

public class TankHealth : MonoBehaviour
{
    [Header("Health")]
    public int maxHealth = 100;
    public Image healthFillImage;
    public Image delayedHealthFillImage;

    [Header("Damage Bar")]
    public float damageDelay = 0.35f;
    public float drainDuration = 0.65f;

    [Header("Health Bar Object")]
    public GameObject healthSlider;

    [Header("Damage Effects")]
    public DamageVolumeTrigger damageVolumeTrigger;
    public GameObject damageBlinkObject;
    public float damageBlinkDuration = 0.12f;

    [Header("Death Effects")]
    public GameObject deathPrefab;
    public Transform deathSpawnPoint;

    [Header("Fall Safety")]
    public float deathYThreshold = -1f;

    [Header("Game Over")]
    public GameObject GameOverPanel;

    [Header("Events")]
    public UnityEvent OnDamage = new UnityEvent();
    public UnityEvent OnDeath = new UnityEvent();

    private int currentHealth;
    private bool isDead;

    private Coroutine delayedBarRoutine;
    private Coroutine damageBlinkRoutine;

    private void Start()
    {
        maxHealth = Mathf.Max(1, maxHealth);
        currentHealth = maxHealth;

        if (damageVolumeTrigger == null)
            damageVolumeTrigger = FindAnyObjectByType<DamageVolumeTrigger>();

        if (damageBlinkObject != null)
            damageBlinkObject.SetActive(false);

        UpdateHealthBar(true);
    }

    private void Update()
    {
        // Automatically trigger death if the tank falls below the level.
        if (!isDead && transform.position.y <= deathYThreshold)
            Die();
    }

    public void takeDamage(int damage)
    {
        if (damage <= 0 || isDead || currentHealth <= 0)
            return;

        currentHealth = Mathf.Max(0, currentHealth - damage);

        UpdateHealthBar(false);

        if (damageVolumeTrigger != null)
            damageVolumeTrigger.TriggerDamage();

        ShowDamageBlink();

        OnDamage.Invoke();

        if (currentHealth <= 0)
        {
            Die();
            return;
        }

        if (delayedBarRoutine != null)
            StopCoroutine(delayedBarRoutine);

        delayedBarRoutine = StartCoroutine(AnimateDelayedBar());
    }

    private void ShowDamageBlink()
    {
        if (damageBlinkObject == null)
            return;

        if (damageBlinkRoutine != null)
            StopCoroutine(damageBlinkRoutine);

        damageBlinkObject.SetActive(true);
        damageBlinkRoutine = StartCoroutine(HideDamageBlink());
    }

    private IEnumerator HideDamageBlink()
    {
        yield return new WaitForSecondsRealtime(
            Mathf.Max(0.01f, damageBlinkDuration)
        );

        if (damageBlinkObject != null)
            damageBlinkObject.SetActive(false);

        damageBlinkRoutine = null;
    }

    private void Die()
    {
        if (isDead)
            return;

        isDead = true;

        if (delayedBarRoutine != null)
        {
            StopCoroutine(delayedBarRoutine);
            delayedBarRoutine = null;
        }

        if (damageBlinkRoutine != null)
        {
            StopCoroutine(damageBlinkRoutine);
            damageBlinkRoutine = null;
        }

        if (damageBlinkObject != null)
            damageBlinkObject.SetActive(false);

        if (healthSlider != null)
            healthSlider.SetActive(false);

        if (deathPrefab != null)
        {
            Transform spawnPoint = deathSpawnPoint != null
                ? deathSpawnPoint
                : transform;

            Instantiate(
                deathPrefab,
                spawnPoint.position,
                spawnPoint.rotation
            );
        }

        if (GameOverPanel != null)
            GameOverPanel.SetActive(true);

        OnDeath.Invoke();

        Destroy(gameObject);
    }

    private void UpdateHealthBar(bool instant)
    {
        float amount = (float)currentHealth / maxHealth;

        if (healthFillImage != null)
            healthFillImage.fillAmount = amount;

        if (instant && delayedHealthFillImage != null)
            delayedHealthFillImage.fillAmount = amount;
    }

    private IEnumerator AnimateDelayedBar()
    {
        yield return new WaitForSeconds(damageDelay);

        if (delayedHealthFillImage == null)
        {
            delayedBarRoutine = null;
            yield break;
        }

        float start = delayedHealthFillImage.fillAmount;
        float target = (float)currentHealth / maxHealth;

        if (start <= target)
        {
            delayedHealthFillImage.fillAmount = target;
            delayedBarRoutine = null;
            yield break;
        }

        float elapsed = 0f;
        float duration = Mathf.Max(0.01f, drainDuration);

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.Clamp01(elapsed / duration);
            t = 1f - Mathf.Pow(1f - t, 3f);

            delayedHealthFillImage.fillAmount =
                Mathf.Lerp(start, target, t);

            yield return null;
        }

        delayedHealthFillImage.fillAmount = target;
        delayedBarRoutine = null;
    }
}