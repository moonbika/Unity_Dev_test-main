using UnityEngine;
using UnityEngine.Events;

public class EnemyTankHealth : MonoBehaviour
{
    [Header("Health")]
    public int maxHealth = 100;
    public GameObject turrent;

    [Header("Death Effects")]
    public GameObject deathPrefab;
    public Transform deathSpawnPoint;
    public float destroyDelay = 0f;

    [Header("Events")]
    public UnityEvent OnDamage = new UnityEvent();
    public UnityEvent OnDeath = new UnityEvent();

    private int currentHealth;
    private EnemyTankAI enemyTankAI;
    private bool isDead;

    private void Start()
    {
        maxHealth = Mathf.Max(1, maxHealth);
        currentHealth = maxHealth;
        enemyTankAI = GetComponent<EnemyTankAI>();
    }

    public void takeDamage(int damage)
    {
        if (isDead || damage <= 0)
            return;

        currentHealth = Mathf.Max(0, currentHealth - damage);
        OnDamage.Invoke();

        if (currentHealth <= 0)
            Die();
    }

    private void Die()
    {
        if (isDead)
            return;

        isDead = true;

        if (enemyTankAI != null)
            enemyTankAI.enabled = false;

        // Spawn explosion / death particle prefab.
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

        // Trigger death event.
        OnDeath.Invoke();

        // Destroy the tank.
        Destroy(gameObject, Mathf.Max(0f, destroyDelay));
    }
}