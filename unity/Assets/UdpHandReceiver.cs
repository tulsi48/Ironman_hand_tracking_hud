using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

[Serializable]
public class HandData
{
    public float x;
    public float y;
    public float z;
    public float angle;
    public float tilt;
    public bool pinch;
}

public class UdpHandReceiver : MonoBehaviour
{
    public int port = 5052;
    public Transform target;

    UdpClient udp;
    IPEndPoint remoteEndPoint;

    void Start()
    {
        udp = new UdpClient(port);
        remoteEndPoint = new IPEndPoint(IPAddress.Any, port);
        udp.Client.ReceiveTimeout = 1;
    }

    void Update()
    {
        try
        {
            if (udp.Available > 0)
            {
                byte[] data = udp.Receive(ref remoteEndPoint);
                string json = Encoding.UTF8.GetString(data);

                HandData hand = JsonUtility.FromJson<HandData>(json);

                if (hand.pinch)
                {
                    // Position
                    float depth = Mathf.Clamp((0.06f - hand.z) * 10f, -2f, 2f);
                    Vector3 pos = new Vector3(
                        (hand.x - 0.5f) * 5f,
                        (0.5f - hand.y) * 5f,
                        depth
                    );
                    target.position = Vector3.Lerp(target.position, pos, 0.2f);

                    // Rotation (Yaw + Pitch)
                    float yaw = -hand.angle;
                    float pitch = Mathf.Clamp(hand.tilt * 90f, -45f, 45f);

                    Quaternion targetRot = Quaternion.Euler(pitch, yaw, 0f);
                    target.rotation = Quaternion.Slerp(target.rotation, targetRot, 0.2f);

                    // Zoom (Scale)
                    float zoom = Mathf.Clamp((0.06f - hand.z) * 5f + 1f, 0.5f, 2.0f);
                    Vector3 targetScale = Vector3.one * zoom;
                    target.localScale = Vector3.Lerp(target.localScale, targetScale, 0.2f);
                }
            }
        }
        catch { }
    }

    void OnApplicationQuit()
    {
        udp.Close();
    }
}
