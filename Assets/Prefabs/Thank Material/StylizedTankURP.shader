Shader "Asse/Stylized Tank URP"
{
    Properties
    {
        [MainTexture] _BaseMap ("Base Map", 2D) = "white" {}
        [MainColor] _BaseColor ("Base Color", Color) = (0.72, 0.76, 0.82, 1)
        [HDR] _TeamColor ("Team Color", Color) = (0.2, 0.9, 0.35, 1)
        _TeamTintStrength ("Team Tint Strength", Range(0, 1)) = 1

        _RampThreshold ("Toon Ramp Threshold", Range(0, 1)) = 0.45
        _RampSmoothness ("Toon Ramp Smoothness", Range(0.001, 0.5)) = 0.08
        _ShadowTint ("Shadow Band Tint", Color) = (0.42, 0.48, 0.58, 1)
        _LitTint ("Lit Band Tint", Color) = (1, 1, 1, 1)
        _AmbientStrength ("Ambient Strength", Range(0, 2)) = 0.7

        [HDR] _RimColor ("Rim Color", Color) = (0.2, 0.9, 1, 1)
        _RimPower ("Rim Power", Range(0.5, 8)) = 3
        _RimIntensity ("Rim Intensity", Range(0, 3)) = 0.65

        [HDR] _SpecularColor ("Specular Color", Color) = (1, 0.9, 0.7, 1)
        _SpecularCutoff ("Specular Cutoff", Range(0, 1)) = 0.72
        _SpecularSmoothness ("Specular Smoothness", Range(0.001, 0.3)) = 0.06
        _SpecularIntensity ("Specular Intensity", Range(0, 2)) = 0.25

        [HDR] _HitFlashColor ("Hit Flash Color", Color) = (1, 1, 1, 1)
        _HitFlashAmount ("Hit Flash Amount", Range(0, 1)) = 0
    }

    SubShader
    {
        Tags
        {
            "RenderPipeline" = "UniversalPipeline"
            "RenderType" = "Opaque"
            "Queue" = "Geometry"
        }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            Cull Back
            ZWrite On
            ZTest LEqual

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_instancing
            #pragma multi_compile_fog
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            // Keep material properties in one UnityPerMaterial CBUFFER for SRP Batcher compatibility.
            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                float4 _BaseColor;
                float4 _TeamColor;
                float _TeamTintStrength;
                float _RampThreshold;
                float _RampSmoothness;
                float4 _ShadowTint;
                float4 _LitTint;
                float _AmbientStrength;
                float4 _RimColor;
                float _RimPower;
                float _RimIntensity;
                float4 _SpecularColor;
                float _SpecularCutoff;
                float _SpecularSmoothness;
                float _SpecularIntensity;
                float4 _HitFlashColor;
                float _HitFlashAmount;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                float3 normalWS : TEXCOORD1;
                float3 viewDirWS : TEXCOORD2;
                float2 uv : TEXCOORD3;
                float4 shadowCoord : TEXCOORD4;
                half fogFactor : TEXCOORD5;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            Varyings Vert(Attributes input)
            {
                Varyings output = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);

                VertexPositionInputs positionInputs = GetVertexPositionInputs(input.positionOS.xyz);
                VertexNormalInputs normalInputs = GetVertexNormalInputs(input.normalOS);

                output.positionCS = positionInputs.positionCS;
                output.positionWS = positionInputs.positionWS;
                output.normalWS = normalInputs.normalWS;
                output.viewDirWS = GetWorldSpaceViewDir(positionInputs.positionWS);
                output.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                output.shadowCoord = GetShadowCoord(positionInputs);
                output.fogFactor = ComputeFogFactor(positionInputs.positionCS.z);
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);

                float3 normalWS = NormalizeNormalPerPixel(input.normalWS);
                float3 viewDirWS = SafeNormalize(input.viewDirWS);
                half4 sampled = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv) * _BaseColor;

                // Blend a team tint over the base texture so one material can retain texture detail.
                float3 baseRGB = lerp(sampled.rgb, sampled.rgb * _TeamColor.rgb, saturate(_TeamTintStrength));

                Light mainLight = GetMainLight(input.shadowCoord);
                float ndotl = saturate(dot(normalWS, mainLight.direction));
                float rampWidth = max(_RampSmoothness, 0.001);
                float toonRamp = smoothstep(_RampThreshold - rampWidth, _RampThreshold + rampWidth, ndotl);

                // The ramp controls the stylized diffuse bands; real shadow attenuation still applies.
                float shadowAtten = mainLight.shadowAttenuation * mainLight.distanceAttenuation;
                float3 bandTint = lerp(_ShadowTint.rgb, _LitTint.rgb, toonRamp);
                float3 directLight = mainLight.color * bandTint * shadowAtten;
                float3 ambientLight = max(SampleSH(normalWS), float3(0.12, 0.12, 0.12)) * _AmbientStrength;
                float3 color = baseRGB * (ambientLight + directLight);

                // Stylized Fresnel rim. Keep intensity modest for a readable top-down silhouette.
                float rimDot = saturate(dot(normalWS, viewDirWS));
                float rim = pow(saturate(1.0 - rimDot), max(_RimPower, 0.001));
                color += _RimColor.rgb * (rim * _RimIntensity);

                // Hard-edged, stylized specular highlight.
                float3 halfDir = SafeNormalize(mainLight.direction + viewDirWS);
                float ndoth = saturate(dot(normalWS, halfDir));
                float specWidth = max(_SpecularSmoothness, 0.001);
                float spec = smoothstep(_SpecularCutoff - specWidth, _SpecularCutoff + specWidth, ndoth);
                color += _SpecularColor.rgb * spec * _SpecularIntensity * mainLight.color * shadowAtten;

                // Drive _HitFlashAmount from 0 to 1 from the damage code (or animate it in the Inspector).
                color = lerp(color, _HitFlashColor.rgb, saturate(_HitFlashAmount));
                color = MixFog(color, input.fogFactor);

                return half4(color, sampled.a);
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex ShadowVert
            #pragma fragment ShadowFrag
            #pragma multi_compile_instancing
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            // Shadows.hlsl in some Unity 2022.3 URP package revisions calls LerpWhiteTo,
            // which is supplied by CommonMaterial.hlsl. Include it explicitly first.
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/CommonMaterial.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"

            float3 _LightDirection;
            float3 _LightPosition;

            struct ShadowAttributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct ShadowVaryings
            {
                float4 positionCS : SV_POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            ShadowVaryings ShadowVert(ShadowAttributes input)
            {
                ShadowVaryings output = (ShadowVaryings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);

                float3 positionWS = TransformObjectToWorld(input.positionOS.xyz);
                float3 normalWS = TransformObjectToWorldNormal(input.normalOS);

                #if defined(_CASTING_PUNCTUAL_LIGHT_SHADOW)
                    float3 lightDirectionWS = normalize(_LightPosition - positionWS);
                #else
                    float3 lightDirectionWS = _LightDirection;
                #endif

                output.positionCS = TransformWorldToHClip(ApplyShadowBias(positionWS, normalWS, lightDirectionWS));
                #if UNITY_REVERSED_Z
                    output.positionCS.z = min(output.positionCS.z, UNITY_NEAR_CLIP_VALUE);
                #else
                    output.positionCS.z = max(output.positionCS.z, UNITY_NEAR_CLIP_VALUE);
                #endif
                return output;
            }

            half4 ShadowFrag(ShadowVaryings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                return 0;
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask 0

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex DepthVert
            #pragma fragment DepthFrag
            #pragma multi_compile_instancing

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct DepthAttributes
            {
                float4 positionOS : POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct DepthVaryings
            {
                float4 positionCS : SV_POSITION;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            DepthVaryings DepthVert(DepthAttributes input)
            {
                DepthVaryings output = (DepthVaryings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, output);
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                return output;
            }

            half4 DepthFrag(DepthVaryings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                return 0;
            }
            ENDHLSL
        }
    }
    FallBack Off
}
