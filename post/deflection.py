import numpy as np

def get_deflected_shape(p1, p2, disp_i, disp_j, v1, v2, v3, scale=1.0, num_points=11):
    """
    Calculates the 'Authentic' deflected shape of a 3D beam element.
    Returns: list of (Position, Tangent, Twist_Angle) tuples.
    """
    
    P1 = np.array(p1)
    P2 = np.array(p2)
    L_vec = P2 - P1
    L = np.linalg.norm(L_vec)
    
    if L < 1e-6: 
                                  
        return [(p1, v1, 0.0), (p2, v1, 0.0)]

    R = np.vstack([v1, v2, v3])
    
    u_global_i = np.array(disp_i[:3]) * scale
    theta_global_i = np.array(disp_i[3:]) * scale
    
    u_local_i = R @ u_global_i      
    theta_local_i = R @ theta_global_i 

    u_global_j = np.array(disp_j[:3]) * scale
    theta_global_j = np.array(disp_j[3:]) * scale
    
    u_local_j = R @ u_global_j
    theta_local_j = R @ theta_global_j

    u1_i, u1_j = u_local_i[0], u_local_j[0]
    
    v_i, v_j = u_local_i[1], u_local_j[1]
    dv_i, dv_j = theta_local_i[2], theta_local_j[2] 

    w_i, w_j = u_local_i[2], u_local_j[2]
    dw_i, dw_j = -theta_local_i[1], -theta_local_j[1]
    
    twist_i = theta_local_i[0]
    twist_j = theta_local_j[0]

    results = [] 
    
    steps = np.linspace(0, 1, num_points)
    
    for s in steps:
                               
        s2 = s * s
        s3 = s * s * s
        x_val = s * L
        
        H1 = 1 - 3*s2 + 2*s3
        H2 = x_val * (1 - s)**2 
        H3 = 3*s2 - 2*s3
        H4 = x_val * (s2 - s)    
        
        dH1 = -6*s + 6*s2
        dH2 = L * (1 - 4*s + 3*s2)
        dH3 = 6*s - 6*s2
        dH4 = L * (3*s2 - 2*s)

        disp_axial = (1-s)*u1_i + s*u1_j
        disp_v = (H1 * v_i) + (H2 * dv_i) + (H3 * v_j) + (H4 * dv_j)
        disp_w = (H1 * w_i) + (H2 * dw_i) + (H3 * w_j) + (H4 * dw_j)
        
        local_pos = np.array([x_val + disp_axial, disp_v, disp_w])
        
        d_axial_ds = L + (u1_j - u1_i)
        
        d_v_ds = (dH1 * v_i) + (dH2 * dv_i) + (dH3 * v_j) + (dH4 * dv_j)
        d_w_ds = (dH1 * w_i) + (dH2 * dw_i) + (dH3 * w_j) + (dH4 * dw_j)
        
        local_tangent = np.array([d_axial_ds, d_v_ds, d_w_ds])
        
        norm_t = np.linalg.norm(local_tangent)
        if norm_t > 1e-9: local_tangent /= norm_t
        else: local_tangent = np.array([1.0, 0, 0])

        global_pos = P1 + (R.T @ local_pos)
        global_tangent = R.T @ local_tangent 
        
        current_twist = (1-s)*twist_i + s*twist_j
        
        results.append((global_pos, global_tangent, current_twist))
        
    return results
