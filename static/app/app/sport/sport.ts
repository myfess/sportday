import { Component, OnInit, ElementRef } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { enableProdMode } from '@angular/core';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpModule } from '@angular/http';
import { UsatuRpcService }     from '../usatu-rpc/usatu-rpc.service';
import { UsatuConfigService } from '../usatu-config/usatu-config.service';


@Component({
    moduleId: module.id,
    selector: 'sport',
    templateUrl: 'sport.html',
    styleUrls: [ 'sport.css' ]
})
export class VkAuthComponent implements OnInit {
    sid_token:string = null;
    user_name:string = null;
    vk_photo:string = null;

    // Страница конкретного пользователя
    member_id = null;
    user_info = null;

    // Страница соревнования
    challenge_id = null;
    challenge_info = null;

    challenges = [];
    current_cat = 'recommend';

    filters = [];

    constructor(
            private rpcService: UsatuRpcService,
            private _config: UsatuConfigService,
            public elementRef: ElementRef
        ) {

        let native = this.elementRef.nativeElement;
        this.sid_token = native.getAttribute("sid-token");
        this.user_name = native.getAttribute("user-name");
        this.vk_photo = native.getAttribute("vk-photo");
        this.member_id = native.getAttribute("member-id");
        this.challenge_id = native.getAttribute("challenge-id");

        if (!this.member_id) {
            this.member_id = null;
        } else {
            this.member_id = parseInt(this.member_id, 10);
        }

        if (!this.challenge_id) {
            this.challenge_id = null;
        } else {
            this.challenge_id = parseInt(this.challenge_id, 10);
        }

        if (!this.sid_token) {
            this.sid_token = null;
        }

        if (!this.vk_photo) {
            this.vk_photo = null;
        }
    }

    ngOnInit(): void {
        if (this.sid_token !== null) {
            $.cookie('usatu_auth', this.sid_token, { expires : 90, path: '/' });
            document.location.href = this.get_domen_url();
            return;
        }

        this.getData();
    }

    switch_category(cat) {
        this.user_info = null;
        this.member_id = null;
        this.current_cat = cat;
        this.getData();
    }

    addFilter(sport) {
        if (this.filters.indexOf(sport) == -1) {
            this.filters.push(sport);
            this.getData();
        } else {
            this.removeFilter(sport);
        }
    }

    removeFilter(sport) {
        let index = this.filters.indexOf(sport);
        if (index > -1) {
            this.filters.splice(index, 1);
            this.getData();
        }
    }

    getData() {
        if (this.member_id) {
            this.rpcService.call(
                'get_challenges_list',
                {
                    'category': 'user',
                    'member_id': this.member_id,
                    'filters': this.filters
                })
                    .then(res => this.challenges = res.challenges);

            // Запросить инфу о пользователе
            this.rpcService.call(
                'get_member_info',
                {
                    'member_id': this.member_id,
                })
                    .then(res =>
                        this.user_info = res.user_info
                    );

            return;
        } else if (this.challenge_id) {
            // Запросить инфу о старте
            this.rpcService.call(
                'get_challenge_info',
                {
                    'challenge_id': this.challenge_id,
                })
                    .then(res =>
                        this.challenge_info = res.challenge_info
                    );
            return;

        }

        this.rpcService.call(
            'get_challenges_list',
            {
                'category': this.current_cat,
                'filters': this.filters
            })
                .then(res => this.challenges = res.challenges);
    }

    set_challenge_part_type(challenge_id, action_type) {
        for (let ch of this.challenges) {
            if (ch.id == challenge_id) {
                ch.part_type = action_type;
                return;
            }
        }
    }

    get_challenge_part_type(challenge_id) {
        for (let ch of this.challenges) {
            if (ch.id == challenge_id) {
                return ch.part_type;
            }
        }
    }

    action(challenge_id, action_type) {
        // сохраняем старый статус для восстановления
        let old_part_type = null;
        let is_set = true;

        for (let ch of this.challenges) {
            if (ch.id == challenge_id) {
                old_part_type = ch.part_type;

                if (old_part_type == action_type) {
                    is_set = false;
                    ch.part_type = null;
                } else {
                    // Сразу устанавливаем новый статус
                    ch.part_type = action_type;
                }
                break;
            }
        }

        this.rpcService.call(
            'challenge_action',
            {
                'id': challenge_id,
                'action': action_type,
                'is_set': is_set
            })
                .then(res =>
                    this.handlerSetPartType(res, challenge_id, old_part_type)
                );
    }

    addFriend(friend_id) {
        let new_status = 'friend';
        if (this.user_info.friend_status == 'friend') {
            new_status = null;
        }

        this.rpcService.call('set_friend_status',{
            'friend_id': friend_id,
            'status': new_status
        }).then(res =>
            this.user_info.friend_status = res.friend_status
        );
    }

    friendButtonText() {
        if (this.user_info.friend_status == 'friend') {
            return 'Удалить из друзья';
        } else {
            return 'Добавить в друзья';
        }
    }

    handlerSetPartType(res, challenge_id, old_part_type) {
        if (!res.challenge_id) {
            // Не удалось обновить - возвращаем обратно
            this.set_challenge_part_type(challenge_id, old_part_type);
        }
    }

    open_vk(): void {
        let url = (
            'https://oauth.vk.com/authorize?client_id=' +
            this.get_vk_app_id() +
            '&display=page&redirect_uri=' +
            this.get_domen_url() +
            '&scope=friends&response_type=code&v=5.103'
        );
        document.location.href = url;
    }

    get_domen_url(): string {
        let domen = this._config.config().DOMEN;
        let url = 'http://' + domen + '/calendar';
        return url
    }

    get_vk_app_id(): string {
        return this._config.config().VK_APP_ID;
    }

    get_russian(sport): string {
        let lang = {
            'ski': 'лыжи',
            'skyrunning': 'скайраннинг',
            'run': 'бег',
            'trail': 'трайл',
            'swim': 'плавание',
            'triathlon': 'триатлон',
            'bicycle': 'велосипед'
        };
        return lang[sport] || sport;
    }

}

@NgModule({
    imports: [
        BrowserModule,
        HttpModule
    ],
    declarations: [VkAuthComponent],
    providers: [UsatuRpcService, UsatuConfigService],
    bootstrap: [VkAuthComponent]
})
export class VkAuthModule { }

let conf = new UsatuConfigService();
if (conf.config().enableProdMode()) {
    enableProdMode();
}

platformBrowserDynamic().bootstrapModule(VkAuthModule);
