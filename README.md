# 🧠 Tello Swarm Control

Progetto di tesi per il controllo algoritmico di uno **sciame di droni DJI Tello**.  

# Struttura del Progetto

── connect.py    # usato per connettere i droni alla rete di laboratorio  
├── docker       # repository contenente il Dockerfile da cui buildare l'immagine  
├── run_c.sh     # script shell che crea un container a partire dall'immagine  
├── run_l.sh     # script shell che crea un container a partire dall'immagine    
├── run.sh       # script shell che crea un container a partire dall'immagine  
├── run_t.sh     # script shell che crea un container a partire dall'immagine  
├── script.sh    # script shell che lancia una build di una immagine docker  
└── src          # repository con i file del progetto  

# Come far partire i nodi
## Build della docker image  
<pre><code>chmod +x build.sh 
./build.sh </code></pre>
> Assicurati gli script siano eseguibili (assegna permessi di esecuzione a tutti gli script shell):
<pre><code>chmod +x run.sh run_l.sh run_t.sh run_c.sh</code></pre>
## Esegui ogni container in un terminale diverso
<pre><code>./run.sh</code></pre>
> Da eseguire per ogni script shell che crea un container. Ogni container andrà a creare un nodo ROS di riferimento

## Esegui nel container 
<pre><code>colcon builld
source install/setup.bash
ros2 run djitello tello</code></pre>
<pre><code>colcon builld
source install/setup.bash
ros2 run djitello controller</code></pre>
> **Opzionale**
<pre><code>colcon builld
source install/setup.bash
ros2 run djitello test</code></pre>
> **Opzionale**
<pre><code>colcon builld
source install/setup.bash
ros2 run djitello logger</code></pre> 
> Per far decollare i droni eseguire in un container:
<pre><code>colcon builld
source install/setup.bash
ros2 service call /tello1/takeoff std_srvs/srv/Trigger & \
ros2 service call /tello2/takeoff std_srvs/srv/Trigger</code></pre> 
> In src/djitello/resource/commonCommands.txt è possibile trovare comandi utili per le chiamate ai servizi
## References
- [ROS 2 documentation](https://docs.ros.org/en/foxy/index.html)  
- [Tello SDK](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)  
- [djitellopy repository](https://github.com/damiafuentes/DJITelloPy)  



