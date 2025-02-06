use riven::consts::PlatformRoute;
use riven::consts::Queue;
use riven::RiotApi;
use std::sync::Arc;
use tokio;
use tokio::task;
use std::env;

#[tokio::main]
async fn main() {
    let api_key = env::var("RIOT_KEY").unwrap();
    let riot_api = Arc::new(RiotApi::new(api_key));

    let ditao1_puuid = match env::var("DITAO_PUUID") {
        Ok(puuid) => puuid,
        _ => panic!("get key")
    };

    let platform = PlatformRoute::NA1;

    let batch_1 = riot_api
        .match_v5()
        .get_match_ids_by_puuid(
            platform.to_regional(),
            ditao1_puuid,
            Some(100),
            None,
            Some(Queue::SUMMONERS_RIFT_5V5_RANKED_FLEX),
            None,
            None,
            None,
        )
        .await
        .unwrap();

    let matches = futures::future::join_all(batch_1.iter().map(|game| {
        let riot_api = riot_api.clone();
        async move {
            riot_api
                .match_v5()
                .get_match(platform.to_regional(), game)
                .await
                .unwrap()
                .unwrap()
        }
    }))
    .await;

    for m in matches {
        println!(
            "{:#?}",
            m.info
                .participants
                .into_iter()
                .map(|a| a.summoner_name)
                .collect::<Vec<_>>()
        );
    }

    // matches.into_iter().filter(|m| {
    //     let sum_names = m
    //         .info
    //         .participants
    //         .iter()
    //         .map(|a| a.summoner_name.clone())
    //         .collect::<Vec<_>>();
    //     sum_names.contains(&"penis".to_string())
    // });

    // let mut games = Vec::new();
    // for game in batch_1 {
    //     let riot_api = riot_api.clone();
    //     games.push(task::spawn(async move {
    //         riot_api
    //             .match_v5()
    //             .get_match(platform.to_regional(), &game)
    //             .await
    //             .unwrap()
    //     }))
    // }

    // println!("here1");
    // let games = futures::future::join_all(games)
    //     .await
    //     .into_iter()
    //     .map(|x| x.unwrap().unwrap())
    //     .collect::<Vec<_>>();
}
