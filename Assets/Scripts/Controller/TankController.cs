using UnityEngine;

public class TankController : MonoBehaviour
{
    [Header("Movement")]
    public float tankSpeed = 15f;
    public float acceleration = 25f;
    public float deceleration = 35f;
    [Range(0.1f, 1f)]
    public float reverseSpeedMultiplier = 0.6f;

    [Header("Rotation")]
    public float tankRotationSpeed = 55f;
    public float turnAcceleration = 140f;
    public float turnDeceleration = 200f;

    [Header("Ground Stability")]
    public float maxUpwardSpeed = 0.25f;

    [Header("Turret")]
    public Transform turretTransform;
    public float turretLagSpeed = 8f;

    [Header("Reticle")]
    public Transform reticleTransform;

    private Rigidbody rb;
    private Tank_Inputs input;

    private Vector3 finalTurretLookDir;
    private float currentTurnSpeed;

    private void Start()
    {
        rb = GetComponent<Rigidbody>();
        input = GetComponent<Tank_Inputs>();

        if (rb != null)
        {
            rb.constraints |= RigidbodyConstraints.FreezeRotationX;
            rb.constraints |= RigidbodyConstraints.FreezeRotationZ;

            rb.interpolation = RigidbodyInterpolation.Interpolate;
            rb.collisionDetectionMode =
                CollisionDetectionMode.ContinuousDynamic;
        }

        if (turretTransform != null)
            finalTurretLookDir = turretTransform.forward;
    }

    private void FixedUpdate()
    {
        if (rb == null || input == null)
            return;

        HandleMovement();
        HandleTurret();
        HandleReticle();
    }

    private void HandleMovement()
    {
        float forwardInput = input.ForwardInput;
        float rotationInput = input.RotationInput;

        // Keep movement horizontal.
        Vector3 forward = Vector3.ProjectOnPlane(
            transform.forward,
            Vector3.up
        ).normalized;

        // Reverse is slower than forward movement.
        float movementInput = forwardInput >= 0f
            ? forwardInput
            : forwardInput * reverseSpeedMultiplier;

        Vector3 targetVelocity = forward * movementInput * tankSpeed;

        // Current horizontal velocity.
        Vector3 currentVelocity = new Vector3(
            rb.linearVelocity.x,
            0f,
            rb.linearVelocity.z
        );

        // Decelerate when releasing movement or reversing direction.
        bool changingDirection =
            currentVelocity.sqrMagnitude > 0.01f &&
            targetVelocity.sqrMagnitude > 0.01f &&
            Vector3.Dot(currentVelocity, targetVelocity) < 0f;

        bool slowingDown =
            targetVelocity.sqrMagnitude < currentVelocity.sqrMagnitude;

        bool noMovementInput = Mathf.Abs(forwardInput) < 0.01f;

        float movementRate =
            noMovementInput || slowingDown || changingDirection
                ? deceleration
                : acceleration;

        Vector3 newVelocity = Vector3.MoveTowards(
            currentVelocity,
            targetVelocity,
            movementRate * Time.fixedDeltaTime
        );

        // Preserve gravity while limiting upward launching.
        float verticalVelocity = Mathf.Min(
            rb.linearVelocity.y,
            maxUpwardSpeed
        );

        rb.linearVelocity = new Vector3(
            newVelocity.x,
            verticalVelocity,
            newVelocity.z
        );

        // Accelerated tank steering.
        float targetTurnSpeed = rotationInput * tankRotationSpeed;

        bool reversingTurn =
            Mathf.Abs(currentTurnSpeed) > 0.01f &&
            Mathf.Abs(targetTurnSpeed) > 0.01f &&
            Mathf.Sign(currentTurnSpeed) != Mathf.Sign(targetTurnSpeed);

        float turnRate =
            Mathf.Abs(rotationInput) < 0.01f || reversingTurn
                ? turnDeceleration
                : turnAcceleration;

        currentTurnSpeed = Mathf.MoveTowards(
            currentTurnSpeed,
            targetTurnSpeed,
            turnRate * Time.fixedDeltaTime
        );

        Quaternion wantedRotation = rb.rotation *
            Quaternion.Euler(
                0f,
                currentTurnSpeed * Time.fixedDeltaTime,
                0f
            );

        rb.MoveRotation(wantedRotation);
    }

    private void HandleTurret()
    {
        if (turretTransform == null)
            return;

        Vector3 lookDirection =
            input.reticlePosition - turretTransform.position;

        lookDirection.y = 0f;

        if (lookDirection.sqrMagnitude < 0.001f)
            return;

        float smooth = 1f - Mathf.Exp(
            -turretLagSpeed * Time.fixedDeltaTime
        );

        finalTurretLookDir = Vector3.Lerp(
            finalTurretLookDir,
            lookDirection,
            smooth
        );

        if (finalTurretLookDir.sqrMagnitude > 0.001f)
        {
            turretTransform.rotation = Quaternion.LookRotation(
                finalTurretLookDir
            );
        }
    }

    private void HandleReticle()
    {
        if (reticleTransform != null)
            reticleTransform.position = input.reticlePosition;
    }
}